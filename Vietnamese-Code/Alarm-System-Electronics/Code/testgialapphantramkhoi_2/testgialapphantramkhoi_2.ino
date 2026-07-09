// ============================================================
//  ĐẦU BÁO KHÓI QUANG — BUỒNG TÁN XẠ GÓC
//  RAK3172 / RUI3 — LoRaWAN OTAA
//  Tuân thủ TCVN 5738:2021 / TCVN 7568-14:2025
//
//  NGUYÊN LÝ BUỒNG TÁN XẠ:
//  - LED phát và LED thu đặt LỆCH GÓC nhau (~120°–135°)
//  - Không có khói → ánh sáng tán xạ ít → ADC thấp (≈ adcCleanRef)
//  - Có khói       → hạt khói tán xạ ánh sáng sang LED thu → ADC TĂNG
//  => ADC_now > ADC_clean khi có khói (NGƯỢC với buồng suy giảm)
//
//  CÔNG THỨC (Beer-Lambert dạng tán xạ):
//  Dựa trên: It = I₀ × exp(−KL)
//  Suy ra:   K  = ln(ADC_now / ADC_clean) / L        [Np/m]
//  Đổi sang dB/m theo TCVN:
//            dB/m = (10 / L) × log10(ADC_now / ADC_clean)
//  Hai dạng tương đương: dB/m = K × (10 / ln(10)) = K × 4.343
//
//  L = khoảng cách từ LED phát đến tâm vùng tán xạ (m)
//  Đo thực tế trên bo mạch, thường 15–35 mm với buồng compact
// ============================================================

#include <Arduino.h>
#include <math.h>

// ============================================================
//  SƠ ĐỒ CHÂN
// ============================================================
#define SMOKE_ADC_PIN       PB2    // Output LMV258 tầng 2 → ADC MCU
#define IR_LED_CTRL_PIN     PA10   // HIGH → transistor NPN dẫn → LED IR sáng
#define LMV258_POWER_PIN    PA15   // HIGH → cấp nguồn LMV258
#define BUZZER_PIN          PA8    // Còi báo động (PWM non-blocking)
#define STATUS_LED_PIN      PA9    // LED trạng thái  
#define TEST_BUTTON_PIN     PA1    // Nút nhấn test / im lặng

// ============================================================
//  LORAWAN OTAA KEYS — điền đúng trước khi deploy
// ============================================================
uint8_t nodeDeviceEUI[8] = {0x41, 0x65, 0x62, 0xDB, 0x1C, 0x97, 0x1C, 0xA5};
uint8_t nodeAppEUI[8]    = {0x12, 0xC0, 0x46, 0x56, 0xBE, 0x8C, 0x91, 0x09};
uint8_t nodeAppKey[16]   = {
  0x58, 0x84, 0x8F, 0xC1, 0xB3, 0xFB, 0x44, 0xAC, 0x40, 0x91, 0xCA, 0xD3, 0x24, 0x1E, 0x46, 0xEB
};

// ============================================================
//  THÔNG SỐ THỜI GIAN — TCVN 5738:2021
// ============================================================
// [TCVN] Thời gian phát hiện tối đa = 40s
// 10s × 4 lần xác nhận = 40s → đúng chuẩn
const uint32_t SLEEP_INTERVAL_MS    = 10000UL;
const uint8_t  SMOKE_CLEAR_COUNT    = 3;   // số lần sạch để tắt alarm

// [TCVN] Hệ thống không dây retry ≤ 60s khi chưa có ACK
const uint32_t RETRY_INTERVAL_MS    = 33000UL;   // retry mỗi 30s
const uint32_t REALARM_INTERVAL_MS  = 300000UL;  // báo cáo định kỳ 5 phút sau ACK
const uint32_t JOIN_RETRY_BACKOFF_MS = 30000UL;  // tránh join dồn dập gây lặp DevNonce

// Chu kỳ đọc ADC trong alarm loop (ms)
const uint32_t ALARM_READ_INTERVAL  = 500UL;
const uint32_t FAST_CHECK_INTERVAL_MS = 500UL;
const uint32_t FAST_CHECK_CONFIRM_MS  = 5000UL;
// ============================================================
//  THÔNG SỐ PHẦN CỨNG CẢM BIẾN
// ============================================================
const uint32_t LMV258_SETTLE_MS  = 50UL;   // LMV258 ổn định sau cấp nguồn
const uint32_t IR_LED_SETTLE_MS  = 80UL;   // LED IR + photodetector ổn định
const uint8_t  ADC_SAMPLES       = 8;      // số mẫu ADC trung bình
const uint32_t ADC_SAMPLE_DELAY  = 3UL;    // delay giữa 2 mẫu (ms)

// ============================================================
//  THÔNG SỐ BUỒNG TÁN XẠ
// ============================================================
//
//  adcCleanRef: ADC đo được khi không khí hoàn toàn sạch
//  → Tự động hiệu chỉnh khi khởi động (calibrateBaseline)
//  → Cần đo lại nếu thay cảm biến hoặc thay đổi mạch khuếch đại
float adcCleanRef = 3700.0f;

//  chamberLengthM: khoảng cách từ LED phát → tâm vùng tán xạ (m)
//  → Đo thực tế trên bo mạch bằng thước kẹp
//  → Nếu không đo được: để 0.025 và điều chỉnh smokeThresholdDbm
//  → Thay đổi giá trị này ảnh hưởng trực tiếp đến kết quả dB/m
float chamberLengthM = 0.035f;   // ví dụ: 2.5 cm, đo lại theo thực tế

//  Ngưỡng báo động [TCVN 7568-14] Loại C: 0.088–0.200 dB/m
//  Bắt đầu với 0.15, điều chỉnh sau khi thử nghiệm thực tế:
//    → Báo nhầm nhiều: tăng lên 0.18–0.20
//    → Phát hiện chậm: giảm xuống 0.10–0.12
const float SMOKE_ALARM_DBM = 0.7f;
const float SMOKE_WARN_DBM  = 0.3f;   // cảnh báo sớm (chỉ log)
const float SMOKE_CLEAR_DBM = 0.2f;
// ============================================================
//  THÔNG SỐ CÒI / NÚT NHẤN
// ============================================================
const uint32_t BUZZER_FREQ_HZ     = 4000UL;
const bool     BUZZER_ACTIVE_HIGH = true;
const uint32_t BUZZER_HALF_US     = 1000000UL / (BUZZER_FREQ_HZ * 2);

const uint32_t BTN_LONG_PRESS_MS  = 2000UL;
const uint32_t BTN_DEBOUNCE_MS    = 50UL;

// ============================================================
//  DEBUG — BẮT BUỘC false khi đo dòng thực tế / sản xuất
// ============================================================
const bool ENABLE_DEBUG = false;
// const bool PLOTTER_DBM_MODE = true;

// ============================================================
//  BIẾN HỆ THỐNG
// ============================================================
int     adcRaw        = 0;
float   smokeK        = 0.0f;   // hệ số tán xạ K (Np/m)
float   smokeDbm      = 0.0f;   // nồng độ khói (dB/m)
bool    smokeDetected = false;
bool    alarmState    = false;
bool    silenceMode   = false;

uint8_t clearCount = 0;

// LoRaWAN
bool     loraJoined   = false;
bool     alarmAcked   = false;
uint32_t lastSendMs   = 0;
bool     lastSendValid = false;
uint32_t nextJoinAttemptMs = 0;

// Còi non-blocking
bool     buzzerRunning = false;
bool     buzzerState   = false;
uint32_t lastBuzzerUs  = 0;

// Nút nhấn
bool     btnStable      = HIGH;
bool     btnReading     = HIGH;
uint32_t btnChangeMs    = 0;
uint32_t btnPressedMs   = 0;
bool     btnLongHandled = false;

uint32_t lastAlarmReadMs = 0;
// Heartbeat LED
uint32_t lastHeartbeatMs = 0;
// Fast smoke check mode
bool fastCheckMode = false;
uint32_t fastCheckStartMs = 0;
// ============================================================
//  KHAI BÁO HÀM
// ============================================================
void  hardwareInit(void);
void  restorePinsAfterWake(void);
void  enterSleep(void);
void  irLedOn(void);
void  irLedOff(void);
void  lmv258On(void);
void  lmv258Off(void);
int   readAdcAverage(uint8_t n);
int   readSensorNormal(void);
int   readSensorAlarm(void);
float calcSmokeK(int adcNow);
float calcSmokeDbm(int adcNow);
bool  isAlarm(float dbm);
float calibrateBaseline(uint8_t n);
void  ledOn(void);
void  ledOff(void);
void  buzzerTick(void);
void  buzzerStop(void);
void  updateButton(void);
void  keepAlarmAlive(void);
void  alarmLoop(void);
void  printState(void);
void  plotDbm(void);
bool  setupLoRaWAN(void);
bool  ensureJoin(void);
bool  sendAlarmPacket(uint16_t adc, float dbm, uint8_t cnt, bool alarmOn);
int readSensorFastCheck(void);
// ============================================================
//  SETUP
// ============================================================
void setup()
{
  hardwareInit();
  api.system.lpm.set(1);

  if (ENABLE_DEBUG)
  {
    Serial.begin(115200);
    delay(300);
    Serial.println("=== ĐẦU BÁO KHÓI TÁN XẠ — RAK3172 ===");
    Serial.println("Buồng góc: ADC GIAM khi co khoi");
    Serial.println("Công thức: K = ln(ADC_clean/ADC_now) / L");
  }

  // Hiệu chỉnh baseline trong không khí sạch
  if (ENABLE_DEBUG) Serial.println("\nHiệu chỉnh baseline...");
  adcCleanRef = calibrateBaseline(10);

  if (ENABLE_DEBUG)
  {
    Serial.print("ADC baseline = ");
    Serial.println(adcCleanRef, 1);
    Serial.print("L = ");
    Serial.print(chamberLengthM * 1000, 1);
    Serial.println(" mm");
  }

  setupLoRaWAN();
}

// ============================================================
//  LOOP CHÍNH
// ============================================================
void loop()
{
  restorePinsAfterWake();
  updateButton();
// Heartbeat LED mỗi 30s
if (millis() - lastHeartbeatMs >= 30000UL)
{
  lastHeartbeatMs = millis();

  ledOn();
  delay(5);
  ledOff();
}
  // Đọc cảm biến
  adcRaw        = readSensorNormal();
  smokeDbm      = calcSmokeDbm(adcRaw);
  smokeK        = calcSmokeK(adcRaw);
  smokeDetected = (smokeDbm >= SMOKE_CLEAR_DBM);

  // Đếm có hysteresis
 // ===============================
// FAST CHECK MODE
// ===============================

// Có dấu hiệu khói
if (smokeDbm >= SMOKE_WARN_DBM)
{
  // Vừa mới vào fast mode
  if (!fastCheckMode)
  {
    fastCheckMode = true;
    fastCheckStartMs = millis();

    if (ENABLE_DEBUG)
      Serial.println(">>> FAST CHECK MODE");
  }

  // Đọc nhanh liên tục
  while (fastCheckMode)
  {
    updateButton();

    adcRaw   = readSensorFastCheck();
    smokeDbm = calcSmokeDbm(adcRaw);
    smokeK   = calcSmokeK(adcRaw);

    plotDbm();
    printState();

    // Khói biến mất
    if (smokeDbm < SMOKE_WARN_DBM)
    {
      fastCheckMode = false;

      if (ENABLE_DEBUG)
        Serial.println("<<< FAST CHECK EXIT");

      break;
    }

    // Có khói mạnh liên tục đủ lâu
    if (smokeDbm >= SMOKE_ALARM_DBM &&
        millis() - fastCheckStartMs >= FAST_CHECK_CONFIRM_MS)
    {
      alarmState = true;
fastCheckMode = false;
      if (ENABLE_DEBUG)
        Serial.println("!!! SMOKE CONFIRMED");

      break;
    }

    delay(FAST_CHECK_INTERVAL_MS);
  }
}

  printState();

  if (alarmState)
    alarmLoop();
  else
  {
    buzzerStop();
    ledOff();
    irLedOff();
    lmv258Off();
    enterSleep();
  }
}

// ============================================================
//  ALARM LOOP — chạy liên tục, không sleep, không delay blocking
// ============================================================
void alarmLoop(void)
{
  if (ENABLE_DEBUG) Serial.println(">>> ALARM");
  ledOn();
  if (!silenceMode) buzzerTick();
  lastAlarmReadMs = millis();

  while (alarmState)
  {
    updateButton();
    ledOn();
    if (!silenceMode) buzzerTick();
    else              buzzerStop();

    // Quản lý gửi LoRaWAN theo TCVN
    uint32_t now = millis();
    bool shouldSend = !lastSendValid
      || (!alarmAcked   && now - lastSendMs >= RETRY_INTERVAL_MS)
      || ( alarmAcked   && now - lastSendMs >= REALARM_INTERVAL_MS);

    if (shouldSend && ensureJoin())
    {
      bool ok = sendAlarmPacket((uint16_t)adcRaw, smokeDbm, 1, true);
      lastSendMs    = millis();
      lastSendValid = true;
      if (ok) alarmAcked = true;
    }

    // Đọc lại cảm biến mỗi 500ms — LED/còi không bị gián đoạn
    if (millis() - lastAlarmReadMs >= ALARM_READ_INTERVAL)
    {
      lastAlarmReadMs = millis();

      adcRaw        = readSensorAlarm();
      smokeDbm      = calcSmokeDbm(adcRaw);
      smokeK        = calcSmokeK(adcRaw);
      smokeDetected = isAlarm(smokeDbm);
      plotDbm();

      if (smokeDetected)
{
  clearCount = 0;
}
else
{
  if (clearCount < 255)
    clearCount++;
}

      printState();

      if (clearCount >= SMOKE_CLEAR_COUNT)
      {
        if (ensureJoin())
        {
          sendAlarmPacket((uint16_t)adcRaw, smokeDbm, clearCount, false);
        }

        alarmState    = false;
        silenceMode   = false;
        alarmAcked    = false;
        lastSendValid = false;
        lastSendMs    = 0;
        clearCount    = 0;
        buzzerStop();
        ledOff();
        irLedOff();
        lmv258Off();
        if (ENABLE_DEBUG) Serial.println("<<< ALARM END");
        break;
      }
    }
  }
}

// ============================================================
//  PHẦN CỨNG
// ============================================================
void hardwareInit(void)
{
  pinMode(IR_LED_CTRL_PIN,  OUTPUT);
  pinMode(LMV258_POWER_PIN, OUTPUT);
  pinMode(BUZZER_PIN,       OUTPUT);
  pinMode(STATUS_LED_PIN,   OUTPUT);
  pinMode(TEST_BUTTON_PIN,  INPUT_PULLUP);
  pinMode(SMOKE_ADC_PIN,    INPUT);
  analogReadResolution(12);

  // -------------------------------------------------------
  //  Tăng drive strength PA8 (BUZZER) lên mức tối đa
  //  STM32WLE5: OSPEEDR = 11 (Very High), OTYPER = 0 (Push-Pull)
  //  → Tăng dòng kéo còi piezo, tiếng to hơn đáng kể
  // -------------------------------------------------------
  GPIOA->OTYPER  &= ~(1U << 8);          // Push-Pull (không open-drain)
  GPIOA->OSPEEDR |=  (3U << (8 * 2));    // Very High Speed trên PA8

  irLedOff(); lmv258Off(); buzzerStop(); ledOff();
}

void restorePinsAfterWake(void)
{
  pinMode(IR_LED_CTRL_PIN,  OUTPUT);
  pinMode(LMV258_POWER_PIN, OUTPUT);
  pinMode(BUZZER_PIN,       OUTPUT);
  pinMode(STATUS_LED_PIN,   OUTPUT);
  pinMode(TEST_BUTTON_PIN,  INPUT_PULLUP);
  pinMode(SMOKE_ADC_PIN,    INPUT);
  analogReadResolution(12);

  // Khôi phục drive strength PA8 sau khi wake (sleep có thể reset)
  GPIOA->OTYPER  &= ~(1U << 8);
  GPIOA->OSPEEDR |=  (3U << (8 * 2));

  irLedOff(); lmv258Off();
  digitalWrite(BUZZER_PIN,     BUZZER_ACTIVE_HIGH ? LOW : HIGH);
  digitalWrite(STATUS_LED_PIN, LOW);
}

void enterSleep(void)
{
  buzzerStop(); ledOff(); irLedOff(); lmv258Off();
  digitalWrite(IR_LED_CTRL_PIN,  LOW);
  digitalWrite(LMV258_POWER_PIN, LOW);
  digitalWrite(BUZZER_PIN,       BUZZER_ACTIVE_HIGH ? LOW : HIGH);
  digitalWrite(STATUS_LED_PIN,   LOW);
  pinMode(STATUS_LED_PIN, INPUT);
  pinMode(BUZZER_PIN,     INPUT);
  pinMode(SMOKE_ADC_PIN,  INPUT);
  if (ENABLE_DEBUG) { Serial.flush(); delay(10); }
  api.system.sleep.all(SLEEP_INTERVAL_MS);
}

void irLedOn(void)  { digitalWrite(IR_LED_CTRL_PIN,  HIGH); }
void irLedOff(void) { digitalWrite(IR_LED_CTRL_PIN,  LOW);  }
void lmv258On(void)  { digitalWrite(LMV258_POWER_PIN, HIGH); }
void lmv258Off(void) { digitalWrite(LMV258_POWER_PIN, LOW);  }

// ============================================================
//  ĐỌC ADC — TRUNG BÌNH N MẪU
// ============================================================
int readAdcAverage(uint8_t n)
{
  long sum = 0;
  for (uint8_t i = 0; i < n; i++)
  {
    sum += analogRead(SMOKE_ADC_PIN);
    delayMicroseconds(200);
  }
  return (int)(sum / n);
}

// ============================================================
//  ĐỌC CẢM BIẾN — CHẾ ĐỘ BÌNH THƯỜNG
//  Trình tự: bật LMV258 → chờ → bật LED IR → chờ → đọc ADC → tắt
// ============================================================
int readSensorNormal(void)
{
  lmv258On();
  delay(LMV258_SETTLE_MS);

  irLedOn();
  delay(IR_LED_SETTLE_MS);

  // Bỏ 2 mẫu đầu (transient sau khi bật)
  analogRead(SMOKE_ADC_PIN);
  analogRead(SMOKE_ADC_PIN);

  int adc = readAdcAverage(ADC_SAMPLES);

  irLedOff();
  delay(5);
  lmv258Off();

  return adc;
}
int readSensorFastCheck(void)
{
  lmv258On();
  delay(LMV258_SETTLE_MS);

  irLedOn();
  delay(IR_LED_SETTLE_MS);

  analogRead(SMOKE_ADC_PIN);
  analogRead(SMOKE_ADC_PIN);

  int adc = readAdcAverage(ADC_SAMPLES);

  irLedOff();
  delay(5);
  lmv258Off();

  return adc;
}
// ============================================================
//  ĐỌC CẢM BIẾN — CHẾ ĐỘ ALARM
//  Dùng while() thay delay() để LED/còi không bị ngắt
// ============================================================
int readSensorAlarm(void)
{
  lmv258On();
  uint32_t t0 = millis();
  while (millis() - t0 < LMV258_SETTLE_MS)
  {
    ledOn();
    if (!silenceMode) buzzerTick(); else buzzerStop();
    updateButton();
  }

  irLedOn();
  t0 = millis();
  while (millis() - t0 < IR_LED_SETTLE_MS)
  {
    ledOn();
    if (!silenceMode) buzzerTick(); else buzzerStop();
    updateButton();
  }

  analogRead(SMOKE_ADC_PIN);
  analogRead(SMOKE_ADC_PIN);
  int adc = readAdcAverage(ADC_SAMPLES);

  irLedOff();
  delay(5);
  lmv258Off();

  return adc;
}

// ============================================================
//  TÍNH TOÁN NỒNG ĐỘ KHÓI — BUỒNG TÁN XẠ
//
//  Dựa trên công thức extinction Beer-Lambert:
//    It = I₀ × exp(−KL)
//  Suy ra:
//    K (Np/m) = ln(ADC_now / ADC_clean) / L
//
//  Đổi sang dB/m theo TCVN (chuẩn đo phổ biến):
//    dB/m = (10 / L) × log10(ADC_now / ADC_clean)
//    dB/m = K × (10 / ln(10)) = K × 4.343
//
//  LƯU Ý BUỒNG TÁN XẠ:
//    - ADC_now > ADC_clean khi có khói (ratio > 1)
//    - Nếu ADC_now <= ADC_clean → không có khói → K = 0, dB/m = 0
// ============================================================
float calcSmokeK(int adcNow)
{
  if (adcNow <= 0)           adcNow = 1;
  if (adcCleanRef <= 0.0f)   adcCleanRef = 1.0f;
  if (chamberLengthM <= 0.0f) return 0.0f;

  // Có khói -> ADC giảm
  if (adcNow >= adcCleanRef)
    return 0.0f;

  float ratio = adcCleanRef / (float)adcNow;

  return logf(ratio) / chamberLengthM;
}

float calcSmokeDbm(int adcNow)
{
  if (adcNow <= 0)           adcNow = 1;
  if (adcCleanRef <= 0.0f)   adcCleanRef = 1.0f;
  if (chamberLengthM <= 0.0f) return 0.0f;

  // Có khói -> ADC giảm
  if (adcNow >= adcCleanRef)
    return 0.0f;

  float ratio = adcCleanRef / (float)adcNow;

  float dbm = (10.0f / chamberLengthM) * log10f(ratio);

  return (dbm < 0.0f) ? 0.0f : dbm;
}

bool isAlarm(float dbm)
{
  return (dbm >= SMOKE_ALARM_DBM);
}

// ============================================================
//  HIỆU CHỈNH BASELINE — đặt thiết bị trong không khí sạch
// ============================================================
float calibrateBaseline(uint8_t n)
{
  long total = 0;
  for (uint8_t i = 0; i < n; i++)
  {
    int adc = readSensorNormal();
    total  += adc;
    if (ENABLE_DEBUG)
    {
      Serial.print("  Mẫu "); Serial.print(i + 1);
      Serial.print(": ADC = "); Serial.println(adc);
    }
    delay(300);
  }

  float baseline = (float)total / n;

  if (ENABLE_DEBUG)
  {
    if (baseline < 10.0f)
      Serial.println("[LỖI] ADC quá thấp! Kiểm tra kết nối LMV258.");
    else if (baseline > 4050.0f)
  Serial.println("[CẢNH BÁO] ADC gan full-scale!");
    else
    {
      Serial.print("Baseline OK: "); Serial.println(baseline, 1);
      Serial.print("K tối thiểu phát hiện = ");
      // K khi ADC = baseline × 1.1 (tăng 10%)
      float kMin = logf(adcCleanRef / (adcCleanRef * 0.9f)) / chamberLengthM;
      Serial.print(kMin, 2); Serial.println(" Np/m");
    }
  }

  return (baseline < 1.0f) ? 1.0f : baseline;
}

// ============================================================
//  LED / CÒI
// ============================================================
void ledOn(void)  { digitalWrite(STATUS_LED_PIN, HIGH); }
void ledOff(void) { digitalWrite(STATUS_LED_PIN, LOW);  }

void buzzerTick(void)
{
  static uint8_t  beepCount = 0;
  static bool     beepOn = true;
  static uint32_t stateStartMs = 0;

  uint32_t nowMs = millis();
  uint32_t nowUs = micros();

  // =========================
  // THỜI GIAN
  // =========================
  const uint32_t BEEP_ON_MS   = 120;   // thời gian kêu
  const uint32_t BEEP_OFF_MS  = 120;   // nghỉ giữa các bip
  const uint32_t PAUSE_MS     = 1000;  // nghỉ sau 3 bip

  // =========================
  // ĐANG KÊU
  // =========================
  if (beepOn)
  {
    // tạo sóng PWM cho còi
    if (nowUs - lastBuzzerUs >= BUZZER_HALF_US)
    {
      lastBuzzerUs = nowUs;
      GPIOA->ODR ^= (1 << 8);
    }

    // hết thời gian bip
    if (nowMs - stateStartMs >= BEEP_ON_MS)
    {
      beepOn = false;
      stateStartMs = nowMs;

      digitalWrite(
        BUZZER_PIN,
        BUZZER_ACTIVE_HIGH ? LOW : HIGH
      );
    }
  }

  // =========================
  // ĐANG NGHỈ
  // =========================
  else
  {
    // sau mỗi bip
    uint32_t waitTime =
      (beepCount >= 2) ? PAUSE_MS : BEEP_OFF_MS;

    if (nowMs - stateStartMs >= waitTime)
    {
      beepOn = true;
      stateStartMs = nowMs;

      beepCount++;

      // đủ 3 bip thì reset
      if (beepCount >= 3)
      {
        beepCount = 0;
      }
    }
  }
}
void buzzerStop(void)
{
  buzzerState = false;

  digitalWrite(
    BUZZER_PIN,
    BUZZER_ACTIVE_HIGH ? LOW : HIGH
  );

  lastBuzzerUs = micros();
}
// ============================================================
//  NÚT NHẤN — giữ 2s để bật chế độ im lặng (silence)
// ============================================================
void updateButton(void)
{
  uint32_t now     = millis();
  bool     reading = digitalRead(TEST_BUTTON_PIN);

  if (reading != btnReading) { btnChangeMs = now; btnReading = reading; }

  if (now - btnChangeMs >= BTN_DEBOUNCE_MS && reading != btnStable)
  {
    btnStable = reading;
    if (btnStable == LOW) { btnPressedMs = now; btnLongHandled = false; }
    else                  { btnPressedMs = 0; }
  }

  if (btnStable == LOW && !btnLongHandled &&
      now - btnPressedMs >= BTN_LONG_PRESS_MS)
  {
    silenceMode    = true;
    btnLongHandled = true;
    if (ENABLE_DEBUG) Serial.println(">> SILENCE ON");
  }
}

void keepAlarmAlive(void)
{
  updateButton();
  ledOn();
  if (!silenceMode) buzzerTick(); else buzzerStop();
}

// ============================================================
//  LORAWANsetupLoRaWAN
// ============================================================
bool setupLoRaWAN(void)
{
  if (!api.lorawan.nwm.set())          return false;
  if (!api.lorawan.njm.set(1))         return false;
  if (!api.lorawan.band.set(9))        return false;   // AS923-2
  if (!api.lorawan.deviceClass.set(0)) return false;   // Class A
  api.lorawan.deui.set(nodeDeviceEUI, 8);
  api.lorawan.appeui.set(nodeAppEUI,  8);
  api.lorawan.appkey.set(nodeAppKey, 16);
  loraJoined = (api.lorawan.njs.get() == 1);
  if (ENABLE_DEBUG) {
    Serial.print("LoRa config OK, NJS=");
    Serial.println(loraJoined ? 1 : 0);
  }
  return true;
}

bool ensureJoin(void)
{
  if (loraJoined || api.lorawan.njs.get() == 1) { loraJoined = true; return true; }
  uint32_t now = millis();
  if (now < nextJoinAttemptMs) return false;

  nextJoinAttemptMs = now + JOIN_RETRY_BACKOFF_MS;
  if (ENABLE_DEBUG) Serial.println("Joining...");
  api.lorawan.join();
  uint32_t t0 = millis();
  while (millis() - t0 < 60000UL)
  {
    keepAlarmAlive();
    if (api.lorawan.njs.get() == 1)
    {
      loraJoined = true;
      nextJoinAttemptMs = 0;
      if (ENABLE_DEBUG) Serial.println("Joined OK");
      return true;
    }
    delay(5);
  }
  loraJoined = false;
  if (ENABLE_DEBUG) Serial.println("Join FAIL");
  return false;
}

// Payload 9 byte:
// [0xA2][ADC_H][ADC_L][DBM×100_H][DBM×100_L][K×100_H][K×100_L][count][alarm]
// 0xA2 = magic byte buồng tán xạ (phân biệt với 0xA1 extinction)
// dB/m × 100 và K × 100 để gửi dạng số nguyên, server chia lại / 100.0
// alarm: 0x01 = on, 0x00 = off
bool sendAlarmPacket(uint16_t adc, float dbm, uint8_t cnt, bool alarmOn)
{
  uint16_t dbm100 = (uint16_t)(dbm  * 100.0f);
  uint16_t k100   = (uint16_t)(smokeK * 100.0f);

  uint8_t payload[9];
  payload[0] = 0xA2;
  payload[1] = (uint8_t)(adc    >> 8);
  payload[2] = (uint8_t)(adc    & 0xFF);
  payload[3] = (uint8_t)(dbm100 >> 8);
  payload[4] = (uint8_t)(dbm100 & 0xFF);
  payload[5] = (uint8_t)(k100   >> 8);
  payload[6] = (uint8_t)(k100   & 0xFF);
  payload[7] = cnt;
  payload[8] = alarmOn ? 0x01 : 0x00;

  bool ok = api.lorawan.send(sizeof(payload), payload, 2, true);

  if (ENABLE_DEBUG)
  {
    Serial.print("Send "); Serial.print(ok ? "OK" : "FAIL");
    Serial.print(" ADC="); Serial.print(adc);
    Serial.print(" dB/m="); Serial.print(dbm, 3);
    Serial.print(" K="); Serial.print(smokeK, 3);
    Serial.print("Np/m Cnt="); Serial.print(cnt);
    Serial.print(" Alarm="); Serial.println(alarmOn ? "ON" : "OFF");
  }
  return ok;
}

void plotDbm(void)
{
  Serial.print("dBm:");
  Serial.print(smokeDbm, 3);
  Serial.print("\tAlarmTh:");
  Serial.print(SMOKE_ALARM_DBM, 3);
  // Serial.print("\tWarnTh:");
  // Serial.print(SMOKE_WARN_DBM, 3);
  // Serial.print("\tYMin:");
  // Serial.print(0.0f, 3);
  // Serial.print("\tYMax:");
  // Serial.println(4.0f, 3);
}

// ============================================================
//  DEBUG PRINT
// ============================================================
void printState(void)
{
  // if (!ENABLE_DEBUG || PLOTTER_DBM_MODE) return;
  Serial.print("ADC=");    Serial.print(adcRaw);
  Serial.print(" K=");     Serial.print(smokeK, 3);   Serial.print("Np/m");
  Serial.print(" dB/m=");  Serial.print(smokeDbm, 3);
  Serial.print(" Det=");   Serial.print(smokeDetected ? "Y" : "N");
  Serial.print(" Clr=");   Serial.print(clearCount);
  Serial.print(" Alarm="); Serial.print(alarmState  ? "ON"  : "OFF");
  Serial.print(" Sil=");   Serial.print(silenceMode  ? "ON"  : "OFF");
  Serial.print(" ACK=");   Serial.print(alarmAcked   ? "Y"   : "N");
  Serial.print(" LoRa=");  Serial.println(loraJoined ? "J"   : "NJ");
  Serial.println(adcRaw);
}
