#ifndef GLOBAL_H
#define GLOBAL_H

#include <Arduino.h>
#include <freertos/FreeRTOS.h>
#include <freertos/semphr.h>

extern const int LDR_PIN;
extern const int LED_PIN;

extern volatile int globalLightValue;   
extern volatile int globalPwmValue;     
extern String globalCmd;                

extern SemaphoreHandle_t serialMutex;

#endif