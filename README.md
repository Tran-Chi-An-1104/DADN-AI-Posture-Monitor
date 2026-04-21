# 🖥️ DADN – Smart Table: AI Workspace Posture Monitor

A real-time IoT posture monitoring system that combines **YOLOv8 image classification**, a **Streamlit** web dashboard, and **YoloBit/ESP32-S3** hardware to detect sitting posture, automatically control desk lighting based on ambient conditions, and push telemetry to **Adafruit IO**.

---

## 📐 System Architecture

```
┌─────────────┐    Serial (USB)    ┌──────────────┐     HTTP/REST     ┌──────────────┐
│   Webcam    │───────────────────▶│              │───────────────────▶│ Adafruit IO  │
│             │                    │   app.py     │                    │  (Cloud)     │
│  YOLOv8 AI  │◀──  CV2 frames    │  Streamlit   │◀── sensor data ───│              │
└─────────────┘                    │  Dashboard   │                    └──────────────┘
                                   └──────┬───────┘
                                          │ Serial commands
                                          │ (0 / 1 / 2)
                                          ▼
                                   ┌──────────────┐
                                   │  YoloBit     │
                                   │  (yolobit.py │
                                   │   / ESP32)   │
                                   │  • LCD1602   │
                                   │  • RGB LEDs  │
                                   │  • Buzzer    │
                                   │  • LED Matrix│
                                   └──────────────┘
```

---

## 🌟 Key Features

| Feature | Description |
|---|---|
| **3-State Posture Detection** | `SITTING_GOOD` (green), `SITTING_BAD` (red), `EMPTY` (idle) — classified by a custom YOLOv8 model (`best.pt`) |
| **85 % Confidence Tolerance** | Minor slouching is forgiven; "Bad Posture" triggers only when confidence ≥ **85 %**, reducing alert fatigue |
| **10-Frame Debounce** | State changes require **10 consecutive stable frames** before the confirmed class is updated, eliminating flicker |
| **Serial Rate Limiting** | Commands are sent to YoloBit only when the state *changes* and at least **1.2 s** apart |
| **Adaptive Desk Lighting** | YoloBit reads an analog light sensor and drives 4 RGB LEDs at 0 / 25 / 50 / 75 / 100 % brightness based on ambient level |
| **LCD Status Display** | A 16×2 LCD shows the current ambient level and LED brightness in real time |
| **Emote & Buzzer Alerts** | The LED matrix displays emotes (😐 / 😊 / 😞) and the buzzer sounds a warning when bad posture is detected |
| **Adafruit IO Integration** | Posture, light, and ambient values are published to cloud feeds every **7 s** for remote monitoring |
| **Modern Streamlit Dashboard** | Live webcam feed, metric cards (Status / Light / Ambient), sidebar controls, and real-time alerts |

---

## 📁 Project Structure

```
DADN - Smart table/
├── app.py              # Streamlit dashboard + AI inference + serial + Adafruit IO
├── yolobit.py          # MicroPython firmware for the YoloBit board
├── best.pt             # Trained YOLOv8 classification model weights
├── requirements.txt    # Python dependencies
├── hardware/
│   └── main.py         # Simplified Micro:bit firmware (UART + display + buzzer pin)
└── YoloBit/            # PlatformIO ESP32-S3 firmware (C++)
    └── src/
        ├── main.cpp            # FreeRTOS task launcher
        ├── YoloBit.cpp         # Core board abstraction
        ├── TaskSensorLED.cpp   # Ambient sensor → LED control task
        ├── TaskLCD.cpp         # LCD1602 display task
        ├── TaskReceiveAI.cpp   # Serial receive from app.py
        ├── TaskFace.cpp        # LED matrix face/emote task
        ├── TaskIOTClient.cpp   # MQTT / IoT client task
        └── TaskTest.cpp        # Hardware test task
```

---

## 🔍 File Details

### `app.py` — Streamlit AI Dashboard

The main desktop application. Runs in the browser via Streamlit.

| Section | Function / Block | Purpose |
|---|---|---|
| **Model Loading** | `load_model()` | Loads `best.pt` (YOLOv8 classifier) with `@st.cache_resource` so it is only loaded once |
| **Serial Reader** | `read_yolobit_data(ser)` | Parses `Lights: XX   Ambient: YY` from YoloBit serial output using regex |
| **Adafruit IO** | `_publish_feed(feed_key, value)` | POSTs a single value to an Adafruit IO feed |
| | `publish_all_feeds(posture, light, ambient)` | Fire-and-forget threaded publish to `smarttable.posture`, `smarttable.led`, `smarttable.ambient` |
| **Sidebar** | — | Camera Start/Stop buttons, confidence toggle, COM port input, YoloBit connect button |
| **Dashboard** | — | Title, 3 metric cards (Status, Light, Ambient), alert banner, live video frame |
| **Camera Loop** | Main `while` loop | Captures frames → YOLO inference → debounce → serial command → draw overlay → update UI → publish to AIO |

#### Inference & Debounce Logic

1. Each frame is classified as `sitting_good`, `sitting_bad`, or `empty`.
2. If `sitting_bad`, confidence must be ≥ **0.85** — otherwise the frame is reclassified as `sitting_good`.
3. A **10-frame debounce** counter tracks consecutive identical raw classes; only after 10 stable frames does `confirmed_class` update.
4. Serial commands (`0` = idle, `1` = good, `2` = bad) are sent to YoloBit only when the confirmed class **changes** and at least **1.2 s** has elapsed since the last send.

---

### `yolobit.py` — MicroPython Firmware

Runs directly on the YoloBit board. Handles sensors, peripheral display, and serial communication with `app.py`.

| Function | Purpose |
|---|---|
| `Sensor2()` | Reads analog light sensor on `pin0`, maps 0–4095 → 0–100 %, displays `Ambient: XX` on LCD row 0 |
| `LED2()` | Adjusts 4 RGB LEDs based on `globalLight` thresholds (≤25 → 100 %, ≤50 → 75 %, ≤65 → 50 %, ≤80 → 25 %, >80 → 0 %), displays brightness on LCD row 1 |
| `read_terminal_input()` | Non-blocking stdin poll using `uselect`; reads serial commands sent by `app.py` |
| `Emote_and_buzzer2()` | Displays LED matrix emotes and plays buzzer based on posture command: `0` → 😐 (CONFUSED, silent), `1` → 😊 (custom smile, silent), `2` → 😞 (SAD, 3× 550 Hz beep) |

#### Main Loop (runs every ~1 s)

```
Sensor2()  →  read_terminal_input()  →  LED2()  →  Emote_and_buzzer2()  →  print status
```

---

### `hardware/main.py` — Micro:bit Firmware (Simplified)

A lightweight alternative to `yolobit.py` for standard Micro:bit boards. Listens on UART at 115200 baud and reacts to single-byte commands:

| Command | Action |
|---|---|
| `'0'` (IDLE) | Display CONFUSED face, buzzer pin OFF |
| `'1'` (GOOD) | Display HAPPY face, buzzer pin OFF |
| `'2'` (BAD) | Display SAD face, buzzer pin ON |

---

## ⚡ Quick Start

### Prerequisites

- Python 3.9+
- A webcam
- *(Optional)* YoloBit board connected via USB serial

### Installation & Run

```bash
# Clone the repository
git clone https://github.com/zKdKaidO/AI-Posture-Monitor.git
cd AI-Posture-Monitor

# Create & activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
streamlit run app.py
```

### Flashing YoloBit Firmware

1. Connect the YoloBit (or Micro:bit) to your PC via USB.
2. Open the board's file manager and copy `yolobit.py` (or `hardware/main.py`) as `main.py` onto the board.
3. Reset the board — it will begin running automatically.

### Flashing ESP32-S3 Firmware (PlatformIO)

```bash
cd YoloBit
pio run --target upload
```

---

## 🔌 Serial Protocol

The serial link between `app.py` and the YoloBit board uses **115200 baud**, transmitting single ASCII characters:

| Direction | Data | Meaning |
|---|---|---|
| **PC → YoloBit** | `'0'` | No person / Idle |
| **PC → YoloBit** | `'1'` | Good posture detected |
| **PC → YoloBit** | `'2'` | Bad posture detected |
| **YoloBit → PC** | `Lights: XX   Ambient: YY` | Current LED brightness (%) and ambient light level (%) |

---

## ☁️ Adafruit IO Feeds

| Feed Key | Value | Update Interval |
|---|---|---|
| `smarttable.posture` | `0` / `1` / `2` | Every 7 s |
| `smarttable.led` | `0`–`100` (LED brightness %) | Every 7 s |
| `smarttable.ambient` | `0`–`100` (ambient light %) | Every 7 s |

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `ultralytics 8.4.21` | YOLOv8 model inference |
| `streamlit` | Web dashboard framework |
| `opencv-python` | Webcam capture & frame drawing |
| `pyserial` | Serial communication with YoloBit |
| `requests` | HTTP client for Adafruit IO REST API |

---

## 📄 License

This project was developed as part of the **Multidisciplinary Project** course at HCMUT.
