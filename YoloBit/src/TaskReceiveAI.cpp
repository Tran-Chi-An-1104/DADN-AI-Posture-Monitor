#include "TaskReceiveAI.h"
#include "global.h"

void taskReceiveAI(void *pvParameters) {
    for (;;) {
        // Kiểm tra xem có dữ liệu từ máy tính (app.py) gửi xuống không
        if (Serial.available() > 0) {
            
            // Chỉ đọc đúng 1 ký tự (char) thay vì đọc nguyên chuỗi String
            char cmd = Serial.read(); 

            // Lấy chìa khóa Mutex để update màn hình an toàn
            if (xSemaphoreTake(serialMutex, portMAX_DELAY) == pdTRUE) {
                if (cmd == '1') {
                    globalCmd = "WARN"; // Nhận b'1': Cảnh báo gù lưng
                    // Ở đây bạn có thể code thêm còi chip (Buzzer) kêu tít tít
                } 
                else if (cmd == '0') {
                    globalCmd = "AUTO"; // Nhận b'0': Ngồi chuẩn
                }
                else if (cmd == '2') {
                    globalCmd = "IDLE"; // Nhận b'2': Không có người
                }
                
                xSemaphoreGive(serialMutex); // Trả chìa khóa
            }
        }
        
        // Ngủ 50ms nhường CPU cho cảm biến và màn hình chạy
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}