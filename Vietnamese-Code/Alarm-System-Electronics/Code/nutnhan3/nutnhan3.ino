// ================== Thong tin ChirpStack ==================
uint8_t devEui[] = {
  0xAE, 0x6C, 0xD1, 0x03, 0x92, 0xD9, 0xA4, 0x07
};

uint8_t appEui[] = {
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

uint8_t appKey[] = {
  0x90, 0xDF, 0x05, 0x36, 0x37, 0x20, 0x2B, 0xAB,
  0xD5, 0x69, 0x1C, 0x9A, 0x63, 0xF6, 0xEA, 0x52
};

// ================== Cau hinh nut nhan/den ==================
#define BUTTON_PIN PA8
#define LED_PIN PA9

bool lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;

uint8_t buttonPressCount = 0;
bool isBlinking = false;
bool ledState = LOW;
unsigned long blinkStartTime = 0;
unsigned long lastBlinkToggleTime = 0;
const unsigned long blinkDurationMs = 3000;
const unsigned long blinkIntervalMs = 200;

const uint8_t uplinkFPort = 1;
const bool uplinkConfirmed = true;
const uint8_t uplinkTrials = 2;
const unsigned long sendRetryMs = 4000;
const unsigned long joinRetryIntervalMs = 10000;

const uint8_t warmupPacketCount = 2;
const unsigned long warmupIntervalMs = 1500;

unsigned long nextJoinAttemptMs = 0;
bool warmupDone = false;
uint8_t warmupSentCount = 0;
unsigned long nextWarmupSendMs = 0;

// Hang doi uplink de tranh mat su kien
const uint8_t TX_QUEUE_SIZE = 6;
char txQueue[TX_QUEUE_SIZE][32];
uint8_t txHead = 0;
uint8_t txTail = 0;
bool txInProgress = false;
unsigned long nextTxAttemptMs = 0;
uint16_t messageId = 0;

bool queueIsEmpty() {
  return txHead == txTail;
}

bool queueIsFull() {
  return ((txTail + 1) % TX_QUEUE_SIZE) == txHead;
}

bool enqueuePayload(const char *payload) {
  if (queueIsFull()) {
    // Drop ban tin cu nhat de uu tien su kien moi
    txHead = (txHead + 1) % TX_QUEUE_SIZE;
  }
  strncpy(txQueue[txTail], payload, sizeof(txQueue[txTail]) - 1);
  txQueue[txTail][sizeof(txQueue[txTail]) - 1] = '\0';
  txTail = (txTail + 1) % TX_QUEUE_SIZE;
  return true;
}

const char *peekPayload() {
  if (queueIsEmpty()) {
    return NULL;
  }
  return txQueue[txHead];
}

void popPayload() {
  if (!queueIsEmpty()) {
    txHead = (txHead + 1) % TX_QUEUE_SIZE;
  }
}

void joinCallback(int32_t status) {
  if (status == 0) {
    Serial.println("[LORA] Join SUCCESS");
  } else {
    Serial.print("[LORA] Join FAILED, status = ");
    Serial.println(status);
  }
}

void sendCallback(int32_t status) {
  Serial.print("[LORA] Send ");
  Serial.println(status == RAK_LORAMAC_STATUS_OK ? "OK" : "FAILED");
}

void tryJoinPeriodic(bool force = false) {
  unsigned long now = millis();
  if (!force && now < nextJoinAttemptMs) {
    return;
  }
  Serial.println("[LORA] Waiting for join...");
  api.lorawan.join();
  nextJoinAttemptMs = millis() + joinRetryIntervalMs;
}

bool sendTextPayload(const char *payload) {
  Serial.print("Dang gui payload: ");
  Serial.println(payload);

  return api.lorawan.send(
    strlen(payload),
    (uint8_t *)payload,
    uplinkFPort,
    uplinkConfirmed,
    uplinkTrials
  );
}

void queueButtonMessage(const char *buttonState) {
  char payload[32];
  messageId++;
  snprintf(payload, sizeof(payload), "{\"button\":\"%s\",\"id\":%u}", buttonState, messageId);
  enqueuePayload(payload);
  nextTxAttemptMs = millis();
}

void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("=== RAK3172 Button Uplink Start ===");

  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  if (api.lorawan.nwm.get() != 1) {
    Serial.print("Set Node device work mode ");
    Serial.println(api.lorawan.nwm.set() ? "Success" : "Fail");
    api.system.reboot();
  }

  if (!api.lorawan.deui.set(devEui, 8)) { Serial.println("[LORA] Set DevEUI FAILED"); return; }
  if (!api.lorawan.appeui.set(appEui, 8)) { Serial.println("[LORA] Set AppEUI FAILED"); return; }
  if (!api.lorawan.appkey.set(appKey, 16)) { Serial.println("[LORA] Set AppKey FAILED"); return; }
  if (!api.lorawan.band.set(9)) { Serial.println("[LORA] Set band FAILED"); return; }
  if (!api.lorawan.deviceClass.set(0)) { Serial.println("[LORA] Set Class A FAILED"); return; }
  if (!api.lorawan.njm.set(1)) { Serial.println("[LORA] Set OTAA FAILED"); return; }

  api.lorawan.adr.set(true);
  api.lorawan.rety.set(2);
  api.lorawan.cfm.set(1);

  api.lorawan.registerJoinCallback(joinCallback);
  api.lorawan.registerSendCallback(sendCallback);

  if (!api.lorawan.join()) {
    Serial.println("[LORA] Join request FAILED");
    return;
  }

  while (api.lorawan.njs.get() == 0) {
    Serial.println("[LORA] Waiting for join...");
    api.lorawan.join();
    delay(10000);
  }

  Serial.println("Join thanh cong!");
  nextWarmupSendMs = millis();
  lastButtonState = digitalRead(BUTTON_PIN);
}

void loop() {
  if (api.lorawan.njs.get() == 0) {
    tryJoinPeriodic();
  }

  if (!warmupDone && api.lorawan.njs.get() == 1) {
    if (millis() >= nextWarmupSendMs) {
      if (sendTextPayload("{\"boot\":\"ok\"}")) {
        warmupSentCount++;
        Serial.print("Da gui goi khoi dong ");
        Serial.print(warmupSentCount);
        Serial.print("/");
        Serial.println(warmupPacketCount);
        if (warmupSentCount >= warmupPacketCount) {
          warmupDone = true;
          Serial.println("Hoan tat khoi dong LoRaWAN, san sang nhan nut.");
        } else {
          nextWarmupSendMs = millis() + warmupIntervalMs;
        }
      } else {
        nextWarmupSendMs = millis() + sendRetryMs;
      }
    }
  }

  if (!queueIsEmpty() && api.lorawan.njs.get() == 1 && millis() >= nextTxAttemptMs) {
    const char *payload = peekPayload();
    if (payload != NULL) {
      txInProgress = true;
      if (sendTextPayload(payload)) {
        popPayload();
        txInProgress = false;
      } else {
        txInProgress = false;
        nextTxAttemptMs = millis() + sendRetryMs;
      }
    }
  }

  if (isBlinking) {
    unsigned long now = millis();
    if (now - blinkStartTime >= blinkDurationMs) {
      isBlinking = false;
      buttonPressCount = 0;
      ledState = LOW;
      digitalWrite(LED_PIN, LOW);
      Serial.println("Da nhap nhay 3s, tat den.");
    } else if (now - lastBlinkToggleTime >= blinkIntervalMs) {
      lastBlinkToggleTime = now;
      ledState = !ledState;
      digitalWrite(LED_PIN, ledState);
    }
  }

  bool currentButtonState = digitalRead(BUTTON_PIN);
  if (lastButtonState == HIGH && currentButtonState == LOW) {
    if (millis() - lastDebounceTime > debounceDelay) {
      lastDebounceTime = millis();
      Serial.println("Da nhan nut!");

      if (!isBlinking) {
        buttonPressCount++;

        if (buttonPressCount == 1) {
          ledState = HIGH;
          digitalWrite(LED_PIN, HIGH);
          queueButtonMessage("ON");
          Serial.println("Lan nhan 1: bat den, queue ON.");
        } else if (buttonPressCount == 2) {
          isBlinking = true;
          blinkStartTime = millis();
          lastBlinkToggleTime = millis();
          ledState = HIGH;
          digitalWrite(LED_PIN, HIGH);
          queueButtonMessage("OFF");
          Serial.println("Lan nhan 2: nhap nhay 3s, queue OFF.");
        }
      }
    }
  }

  lastButtonState = currentButtonState;
  delay(10);
}
