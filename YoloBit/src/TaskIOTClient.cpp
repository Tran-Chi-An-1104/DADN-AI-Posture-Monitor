#include "TaskIOTClient.h"
#include "global.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

const char* WIFI_SSID = "..."; 
const char* WIFI_PASS = "ohmygodd";      
const char* MQTT_SERVER = "app.coreiot.io";
const int   MQTT_PORT   = 1883;         
const char* MQTT_CLIENT_ID = "SmartTable"; 
const char* MQTT_USERNAME  = "tranchianzero";           
const char* MQTT_PASSWORD  = "tranchianzero";           

const char* TB_TELEMETRY_TOPIC = "v1/devices/me/telemetry";

WiFiClient espClient;
PubSubClient mqtt(espClient);

unsigned long lastReconnectAttempt = 0;

void taskIOTClient(void *pvParameters) {
    WiFi.mode(WIFI_STA); 
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    
    mqtt.setServer(MQTT_SERVER, MQTT_PORT);
    
    unsigned long lastSendTime = 0;

    for (;;) {
        if (WiFi.status() != WL_CONNECTED) {
            vTaskDelay(pdMS_TO_TICKS(500));
            continue; 
        }
        if (!mqtt.connected()) {
            unsigned long now = millis();
            if (now - lastReconnectAttempt > 5000) {
                lastReconnectAttempt = now;
                Serial.print("[MQTT] Dang ket noi CoreIoT... ");
                if (mqtt.connect(MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD)) {
                    Serial.println("Thanh cong!");
                } else {
                    Serial.print("That bai (ma loi: ");
                    Serial.print(mqtt.state());
                    Serial.println("). Se thu lai sau 5s");
                }
            }
        } else {
            mqtt.loop();

            if (millis() - lastSendTime > 2000) {
                String currentStatus;
                if (xSemaphoreTake(serialMutex, portMAX_DELAY) == pdTRUE) {
                    currentStatus = globalCmd;
                    xSemaphoreGive(serialMutex);
                }

                JsonDocument doc;
                doc["light_lux"] = globalLightValue;  
                doc["led_pwm"]   = globalPwmValue;    
                doc["status"]    = currentStatus;     

                char jsonBuffer[256];
                serializeJson(doc, jsonBuffer);

                mqtt.publish(TB_TELEMETRY_TOPIC, jsonBuffer);
                lastSendTime = millis();
            }
        }
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}