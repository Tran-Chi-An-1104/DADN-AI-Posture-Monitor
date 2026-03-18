#include <Arduino.h>
#include "global.h"
#include "TaskSensorLED.h"
#include "TaskLCD.h"

const int LDR_PIN = 34;
const int LED_PIN = 25;

volatile int globalLightValue = 0;
volatile int globalPwmValue = 0;
String globalCmd = "AUTO";

// Định nghĩa biến Mutex
SemaphoreHandle_t serialMutex;

void setup() {
    Serial.begin(115200);

    // Tạo Mutex
    serialMutex = xSemaphoreCreateMutex();
    
    // Kiểm tra xem Mutex có tạo thành công không
    if (serialMutex != NULL) {
        Serial.println("\n[SYSTEM] Mutex khoi tao thanh cong!");
    }

    Serial.println("[SYSTEM] Dang khoi dong cac Task...");

    xTaskCreatePinnedToCore(taskSensorAndLED, "Task_Sensor_LED", 4096, NULL, 1, NULL, 1);
    xTaskCreatePinnedToCore(taskLCD, "Task_LCD", 4096, NULL, 1, NULL, 0);
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(1000));
}