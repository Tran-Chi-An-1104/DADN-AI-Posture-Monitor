#include "TaskSensorLED.h"
#include "global.h"

const int PWM_FREQ = 5000;
const int PWM_CHANNEL = 0;
const int PWM_RES = 8;

void taskSensorAndLED(void *pvParameters) {
    ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RES);
    ledcAttachPin(LED_PIN, PWM_CHANNEL);

    int printCounter = 0; // Bộ đếm để giảm tốc độ in Serial

    for (;;) {
        int currentLight = analogRead(LDR_PIN);
        int calculatedPwm = map(currentLight, 0, 4095, 255, 0);
        calculatedPwm = constrain(calculatedPwm, 0, 255);
        
        ledcWrite(PWM_CHANNEL, calculatedPwm);

        globalLightValue = currentLight;
        globalPwmValue = calculatedPwm;

        // Cứ mỗi 10 vòng lặp (10 * 50ms = 500ms) thì in log 1 lần
        printCounter++;
        if (printCounter >= 10) {
            // Lấy chìa khóa Mutex (Chờ tối đa portMAX_DELAY)
            if (xSemaphoreTake(serialMutex, portMAX_DELAY) == pdTRUE) {
                Serial.printf("[CORE 1 - SENSOR] Lux: %d | PWM: %d\n", currentLight, calculatedPwm);
                xSemaphoreGive(serialMutex); // In xong trả lại chìa khóa
            }
            printCounter = 0; // Reset bộ đếm
        }

        vTaskDelay(pdMS_TO_TICKS(50));
    }
}