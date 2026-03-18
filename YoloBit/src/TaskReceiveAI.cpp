#include "TaskReceiveAI.h"
#include "global.h"

void taskReceiveAI(void *pvParameters) {
    for (;;) {
        if (Serial.available() > 0) {
            char cmd = Serial.read(); 
            if (xSemaphoreTake(serialMutex, portMAX_DELAY) == pdTRUE) {
                if (cmd == '1') {
                    globalCmd = "WARN"; // Nhận b'1': Cảnh báo gù lưng
                    if ((millis() / 200) % 2 == 0) {
                        digitalWrite(BUZZER_PIN, HIGH);
                    }
                } 
                else if (cmd == '0') {
                    globalCmd = "AUTO"; // Nhận b'0': Ngồi chuẩn
                    digitalWrite(BUZZER_PIN, LOW);
                }
                else if (cmd == '2') {
                    globalCmd = "IDLE"; // Nhận b'2': Không có người
                    digitalWrite(BUZZER_PIN, LOW);
                }
                
                xSemaphoreGive(serialMutex);
            }
        }
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}