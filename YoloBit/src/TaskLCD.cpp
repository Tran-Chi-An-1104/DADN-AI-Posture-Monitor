#include "TaskLCD.h"
#include "global.h"

LiquidCrystal_I2C lcd(0x27, 16, 2); 

void taskLCD(void *pvParameters) {
    lcd.init();
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Smart Table OK!");
    
    // In log khởi tạo thành công
    if (xSemaphoreTake(serialMutex, portMAX_DELAY) == pdTRUE) {
        Serial.println("[CORE 0 - LCD  ] Khoi tao man hinh thanh cong.");
        xSemaphoreGive(serialMutex);
    }

    vTaskDelay(pdMS_TO_TICKS(1500));
    lcd.clear();

    for (;;) {
        int light = globalLightValue;
        int pwm = globalPwmValue;
        int lightPercent = map(pwm, 0, 255, 0, 100);

        // Hiển thị lên LCD
        lcd.setCursor(0, 0);
        lcd.print("CMD:");
        lcd.print(globalCmd);
        lcd.print(" LED:");
        if(lightPercent < 10) lcd.print(" "); 
        if(lightPercent < 100) lcd.print(" ");
        lcd.print(lightPercent);
        lcd.print("%");

        lcd.setCursor(0, 1);
        lcd.print("Lux:");
        lcd.print(light);
        lcd.print("    "); 

        // In trạng thái ra Serial
        if (xSemaphoreTake(serialMutex, portMAX_DELAY) == pdTRUE) {
            Serial.printf("[CORE 0 - LCD  ] Dang hien thi -> CMD: %s | LED: %d%%\n", globalCmd.c_str(), lightPercent);
            xSemaphoreGive(serialMutex);
        }

        vTaskDelay(pdMS_TO_TICKS(500));
    }
}