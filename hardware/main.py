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
            
            # --- XỬ LÝ LỆNH ---
            if char == '1': # SITTING_BAD
                display.show(Image.SAD)    # Hiện mặt mếu
                pin0.write_digital(1)      # Kích điện chân số 0 (Còi kêu)
                
            elif char == '0': # SITTING_GOOD
                display.show(Image.HAPPY)  # Hiện mặt cười
                pin0.write_digital(0)      # Ngắt điện chân số 0 (Còi tắt)
                
            elif char == '2': # EMPTY (Không có người)
                display.clear()            # Tắt sạch màn hình LED
                pin0.write_digital(0)      # Tắt còi
                
    sleep(100) # Nghỉ 100ms cho mạch đỡ nóng