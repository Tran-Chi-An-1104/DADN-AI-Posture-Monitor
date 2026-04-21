#include "TaskTest.h"
#include <Arduino.h>

void taskTestLED(void *pvParameters) {
    const int TEST_LED_PIN = 1;
    pinMode(TEST_LED_PIN, OUTPUT);
    digitalWrite(TEST_LED_PIN, LOW);
    
    Serial.println("\n[TEST] LED blink test started on pin 1 - Toggle every 2 seconds\n");
    
    for (;;) {
        // LED ON
        digitalWrite(TEST_LED_PIN, HIGH);
        Serial.println("[TEST] LED ON");
        vTaskDelay(pdMS_TO_TICKS(2000));  // 2 seconds
        
        // LED OFF
        digitalWrite(TEST_LED_PIN, LOW);
        Serial.println("[TEST] LED OFF");
        vTaskDelay(pdMS_TO_TICKS(2000));  // 2 seconds
    }
}
