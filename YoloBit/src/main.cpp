#include <Arduino.h>
#include "global.h"
#include "TaskSensorLED.h"
#include "TaskLCD.h"
#include "TaskReceiveAI.h"
#include "TaskFace.h"
#include "TaskIOTClient.h"

const int LDR_PIN = 34; //34
const int LED_PIN = 25; //25
const int BUZZER_PIN = 26;

volatile int globalLightValue = 0;
volatile int globalPwmValue = 0;
String globalCmd = "...";
SemaphoreHandle_t serialMutex;

void setup() {
    Serial.begin(115200);
    delay(2000);
    serialMutex = xSemaphoreCreateMutex();

    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);
    
    xTaskCreatePinnedToCore(taskReceiveAI, "Task_Receive_AI", 4096, NULL, 1, NULL, 1);
    xTaskCreatePinnedToCore(taskSensorAndLED, "Task_Sensor_LED", 4096, NULL, 1, NULL, 1);
    xTaskCreatePinnedToCore(taskLCD, "Task_LCD", 4096, NULL, 1, NULL, 0);
    xTaskCreatePinnedToCore(taskFace, "Task_Face", 4096, NULL, 1, NULL, 0);
    xTaskCreatePinnedToCore(taskIOTClient, "Task_IOT", 8192, NULL, 1, NULL, 0);
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(1000));
}