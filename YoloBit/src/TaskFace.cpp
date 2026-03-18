#include "TaskFace.h"
#include "global.h"
#include <Adafruit_NeoPixel.h>
#define MATRIX_PIN 27 
#define NUMPIXELS 25

Adafruit_NeoPixel pixels(NUMPIXELS, MATRIX_PIN, NEO_GRB + NEO_KHZ800);
const int faceHappy[25] = {
  0, 1, 0, 1, 0,
  0, 0, 0, 0, 0,
  0, 0, 0, 0, 0,
  1, 0, 0, 0, 1,
  0, 1, 1, 1, 0
};
const int faceSad[25] = {
  0, 1, 0, 1, 0,
  0, 0, 0, 0, 0,
  0, 0, 0, 0, 0,
  0, 1, 1, 1, 0,
  1, 0, 0, 0, 1
};

void drawFace(const int faceMap[], uint32_t color) {
    pixels.clear();
    for (int i = 0; i < 25; i++) {
        if (faceMap[i] == 1) {
            pixels.setPixelColor(i, color);
        }
    }
    pixels.show();
}

void taskFace(void *pvParameters) {
    pixels.begin();
    pixels.setBrightness(30); 
    pixels.show(); 

    for (;;) {
        if (globalCmd == "WARN") {
            drawFace(faceSad, pixels.Color(255, 0, 0));
        } 
        else if (globalCmd == "AUTO") {
            drawFace(faceHappy, pixels.Color(0, 255, 0));
        }
        else if (globalCmd == "IDLE") {
            pixels.clear();
            pixels.show();
        }
        vTaskDelay(pdMS_TO_TICKS(200));
    }
}