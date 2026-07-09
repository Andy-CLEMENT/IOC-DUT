#include <Arduino.h>

// =========================
// Chân điều khiển
// =========================
#define ALARM_PIN   PB3

// =========================
// OTAA Keys
// =========================
#define OTAA_BAND     (RAK_REGION_AS923_2)
#define OTAA_DEVEUI   {0xAC, 0x1F, 0x09, 0xFF, 0xFE, 0x1D, 0x69, 0xEF}
#define OTAA_APPEUI   {0xAC, 0x1F, 0x09, 0xFF, 0xF9, 0x15, 0x31, 0x72}
#define OTAA_APPKEY   {0xAC, 0x1F, 0x09, 0xFF, 0xFE, 0x1D, 0x69, 0xEF, \
                       0xAC, 0x1F, 0x09, 0xFF, 0xF9, 0x15, 0x31, 0x72}

// =========================
// Config
// =========================
#define REPORT_PERIOD   30000

bool g_alarm_on       = false;
unsigned long lastReportMs = 0;

// =========================
// Điều khiển ALARM
// =========================
void alarmOn() {
  digitalWrite(ALARM_PIN, HIGH);
  g_alarm_on = true;
  Serial.println("[CTRL] ALARM ON");
}

void alarmOff() {
  digitalWrite(ALARM_PIN, LOW);
  g_alarm_on = false;
  Serial.println("[CTRL] ALARM OFF");
}

// =========================
// Callback nhận downlink
// =========================
void receiveCallback(SERVICE_LORA_RECEIVE_T *data)
{
  if (data == NULL) return;

  Serial.println("===== DOWNLINK RECEIVED =====");
  Serial.printf("fPort : %d\r\n", data->Port);
  Serial.printf("RSSI  : %d\r\n", data->Rssi);
  Serial.printf("SNR   : %d\r\n", data->Snr);
  Serial.printf("Size  : %d\r\n", data->BufferSize);

  if (data->BufferSize > 0) {
    Serial.print("HEX   : ");
    for (int i = 0; i < data->BufferSize; i++) {
      Serial.printf("%02X ", data->Buffer[i]);
    }
    Serial.println();
  }

  // Chỉ xử lý fPort 10
  if (data->Port != 10) {
    Serial.println("[CTRL] Wrong fPort, ignored");
    return;
  }

  if (data->BufferSize > 0) {
    uint8_t cmd = data->Buffer[0];
    if      (cmd == 0x01) alarmOn();
    else if (cmd == 0x00) alarmOff();
    else    Serial.printf("[CTRL] Unknown cmd: 0x%02X\r\n", cmd);
  }
}

// =========================
// Callback join
// =========================
void joinCallback(int32_t status)
{
  if (status == 0) {
    Serial.println("[LORA] Join SUCCESS");
  } else {
    Serial.printf("[LORA] Join FAILED, status = %d\r\n", status);
  }
}

// =========================
// Callback gửi
// =========================
void sendCallback(int32_t status)
{
  Serial.printf("[LORA] Send %s\r\n",
    status == RAK_LORAMAC_STATUS_OK ? "OK" : "FAILED");
}

// =========================
// Gửi trạng thái uplink
// =========================
void sendStatusUplink()
{
  char payload[32];
  snprintf(payload, sizeof(payload),
           "{\"alarm\":\"%s\"}", g_alarm_on ? "ON" : "OFF");

  Serial.printf("[LORA] Uplink: %s\r\n", payload);

  if (!api.lorawan.send(strlen(payload), (uint8_t *)payload, 2, false, 1)) {
    Serial.println("[LORA] Send request failed");
  }
}

// =========================
// Setup
// =========================
void setup()
{
  Serial.begin(115200, RAK_AT_MODE);
  delay(2000);

  Serial.println("========== DEVICE START ==========");
  Serial.println("Band  : AS923-2");
  Serial.println("Class : C");
  Serial.println("Pin   : PA1");
  Serial.println("==================================");

  pinMode(ALARM_PIN, OUTPUT);
  alarmOff();

  // --- Cấu hình LoRaWAN (theo pattern code 2) ---
  if (api.lorawan.nwm.get() != 1) {
    Serial.printf("Set Node device work mode %s\r\n",
      api.lorawan.nwm.set() ? "Success" : "Fail");
    api.system.reboot();
  }

  uint8_t node_device_eui[8] = OTAA_DEVEUI;
  uint8_t node_app_eui[8]    = OTAA_APPEUI;
  uint8_t node_app_key[16]   = OTAA_APPKEY;

  if (!api.lorawan.deui.set(node_device_eui, 8)) {
    Serial.println("[LORA] Set DevEUI FAILED"); return;
  }
  if (!api.lorawan.appeui.set(node_app_eui, 8)) {
    Serial.println("[LORA] Set AppEUI FAILED"); return;
  }
  if (!api.lorawan.appkey.set(node_app_key, 16)) {
    Serial.println("[LORA] Set AppKey FAILED"); return;
  }
  if (!api.lorawan.band.set(OTAA_BAND)) {
    Serial.println("[LORA] Set band FAILED"); return;
  }
  if (!api.lorawan.deviceClass.set(RAK_LORA_CLASS_C)) {
    Serial.println("[LORA] Set Class C FAILED"); return;
  }
  if (!api.lorawan.njm.set(RAK_LORA_OTAA)) {
    Serial.println("[LORA] Set OTAA FAILED"); return;
  }

  api.lorawan.adr.set(true);
  api.lorawan.rety.set(1);
  api.lorawan.cfm.set(0);

  api.lorawan.registerRecvCallback(receiveCallback);
  api.lorawan.registerJoinCallback(joinCallback);
  api.lorawan.registerSendCallback(sendCallback);

  if (!api.lorawan.join()) {
    Serial.println("[LORA] Join request FAILED"); return;
  }

  // Chờ join thành công
  while (api.lorawan.njs.get() == 0) {
    Serial.println("[LORA] Waiting for join...");
    api.lorawan.join();
    delay(10000);
  }

  Serial.println("[LORA] Joined! Device ready.");
  Serial.printf("[LORA] Band: %d\r\n", api.lorawan.band.get());
}

// =========================
// Loop
// =========================
void loop()
{
  if (millis() - lastReportMs >= REPORT_PERIOD) {
    lastReportMs = millis();
    sendStatusUplink();
  }

  delay(50);
}