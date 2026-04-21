from microbit import *

# Khởi tạo cổng giao tiếp USB (UART) với tốc độ 115200 (Khớp với app.py)
uart.init(baudrate=115200)

# Hiện mặt cười báo hiệu mạch đã sẵn sàng
display.show(Image.HAPPY)

while True:
    # Nếu có tin nhắn từ máy tính gửi xuống
    if uart.any():
        data = uart.read(1) # Đọc 1 byte
        if data:
            char = chr(data[0])
            
            # --- XỬ LÝ LỆNH (khớp app.py / yolobit: 0=IDLE, 1=GOOD, 2=BAD) ---
            if char == '0':  # IDLE
                display.show(Image.CONFUSED)
                pin0.write_digital(0)

            elif char == '1':  # GOOD
                display.show(Image.HAPPY)
                pin0.write_digital(0)

            elif char == '2':  # BAD
                display.show(Image.SAD)
                pin0.write_digital(1)
                
    sleep(100) # Nghỉ 100ms cho mạch đỡ nóng