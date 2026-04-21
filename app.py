import cv2
import streamlit as st
from ultralytics import YOLO
import serial
import re
import time
import requests
import threading

# ==========================================
# 1. PAGE CONFIGURATION & SESSION STATE
# ==========================================
st.set_page_config(
    page_title="AI Posture Monitor",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "camera_running" not in st.session_state:
    st.session_state.camera_running = False
if "ser" not in st.session_state:
    st.session_state.ser = None
if "last_serial_cmd" not in st.session_state:
    st.session_state.last_serial_cmd = None
if "last_serial_time" not in st.session_state:
    st.session_state.last_serial_time = 0.0
if "pending_class" not in st.session_state:
    st.session_state.pending_class = "empty"
if "stable_frame_count" not in st.session_state:
    st.session_state.stable_frame_count = 0
if "confirmed_class" not in st.session_state:
    st.session_state.confirmed_class = "empty"
if "light_value" not in st.session_state:
    st.session_state.light_value = "N/A"
if "ambient_value" not in st.session_state:
    st.session_state.ambient_value = "N/A"
if "last_aio_publish" not in st.session_state:
    st.session_state.last_aio_publish = 0.0

# ==========================================
# 2. MODEL LOADING
# ==========================================
@st.cache_resource(show_spinner="Loading AI Model...")
def load_model():
    return YOLO("best.pt")

model = load_model()

# ==========================================
# 3. HELPER: READ YOLOBIT SERIAL DATA
# ==========================================
def read_yolobit_data(ser):
    """Parse 'Lights: XX   Ambient: YY' from YoloBit serial output."""
    light = None
    ambient = None
    try:
        while ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            m_light = re.search(r'Lights:\s*(\d+)', line)
            m_ambient = re.search(r'Ambient:\s*(\d+)', line)
            if m_light:
                light = m_light.group(1)
            if m_ambient:
                ambient = m_ambient.group(1)
    except Exception:
        pass
    return light, ambient

# ==========================================
# 4. ADAFRUIT IO
# ==========================================
AIO_USERNAME = "tranchianzero"
AIO_KEY      = "aio_VxPm82DRT6O8u70uRdP6anoqekUr"
AIO_BASE_URL = f"https://io.adafruit.com/api/v2/{AIO_USERNAME}/feeds"
AIO_HEADERS  = {"X-AIO-Key": AIO_KEY, "Content-Type": "application/json"}
AIO_PUBLISH_INTERVAL = 7

def _publish_feed(feed_key, value):
    try:
        requests.post(
            f"{AIO_BASE_URL}/{feed_key}/data",
            json={"value": value},
            headers=AIO_HEADERS,
            timeout=3,
        )
    except Exception:
        pass

def publish_all_feeds(posture, light, ambient):
    """Fire-and-forget publish to all Adafruit IO feeds."""
    def _worker():
        _publish_feed("smarttable.posture", posture)
        if light != "N/A":
            _publish_feed("smarttable.led", light)
        if ambient != "N/A":
            _publish_feed("smarttable.ambient", ambient)
    threading.Thread(target=_worker, daemon=True).start()

# ==========================================
# 5. SIDEBAR: CONTROLS & SETTINGS
# ==========================================
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.markdown("Configure your posture monitor settings below.")

    st.subheader("Display Settings")
    show_confidence = st.checkbox("Show Confidence Score (%)", value=True)

    st.markdown("---")
    st.subheader("Camera Controls")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start", use_container_width=True, type="primary"):
            st.session_state.camera_running = True
            st.rerun()
    with col2:
        if st.button("⏹️ Stop", use_container_width=True, type="secondary"):
            st.session_state.camera_running = False
            st.rerun()

    st.markdown("---")
    st.subheader("🔌 YoloBit Connection")
    com_port = st.text_input("COM Port", placeholder="e.g., COM3")

    if st.button("Connect YoloBit", use_container_width=True):
        try:
            st.session_state.ser = serial.Serial(com_port, 115200, timeout=0.1)
            st.sidebar.success(f"✅ Connected to {com_port}")
        except Exception:
            st.sidebar.error("❌ Connection failed! Check COM port.")

    st.markdown("---")
    st.info("💡 **Note:** The system uses an 85% confidence tolerance. Mild slouching might be forgiven to prevent alert fatigue.")

# ==========================================
# 6. MAIN DASHBOARD AREA
# ==========================================
st.title("🖥️ AI Workspace Posture Monitor")
st.markdown("Real-time classification system analyzing your sitting posture.")

col_status, col_light, col_ambient = st.columns(3)
with col_status:
    status_placeholder = st.empty()
with col_light:
    light_placeholder = st.empty()
with col_ambient:
    ambient_placeholder = st.empty()

status_placeholder.metric("📊 Status", "IDLE")
light_placeholder.metric("💡 Light", st.session_state.light_value)
ambient_placeholder.metric("🌤️ Ambient", st.session_state.ambient_value)

alert_placeholder = st.empty()
frame_placeholder = st.empty()

# ==========================================
# 7. CAMERA PROCESSING LOOP
# ==========================================
if st.session_state.camera_running:
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        st.error("❌ Error: Could not access the webcam. Please check your device permissions.")
        st.session_state.camera_running = False

    DEBOUNCE_FRAMES = 10
    SERIAL_MIN_INTERVAL = 1.2

    # Send initial IDLE to YoloBit
    if st.session_state.camera_running and st.session_state.ser and st.session_state.ser.is_open:
        try:
            st.session_state.ser.write(b'0')
            st.session_state.last_serial_cmd = b'0'
            st.session_state.last_serial_time = time.time()
        except Exception:
            pass

    while st.session_state.camera_running:
        success, frame = cap.read()
        if not success:
            alert_placeholder.error("❌ Error: Failed to read frame from webcam.")
            break

        # --- Read YoloBit sensor data ---
        if st.session_state.ser and st.session_state.ser.is_open:
            light, ambient = read_yolobit_data(st.session_state.ser)
            if light is not None:
                st.session_state.light_value = f"{light}%"
            if ambient is not None:
                st.session_state.ambient_value = f"{ambient}%"
            light_placeholder.metric("💡 Light", st.session_state.light_value)
            ambient_placeholder.metric("🌤️ Ambient", st.session_state.ambient_value)

        # --- AI Inference ---
        results = model.predict(frame, verbose=False)

        raw_class = "empty"
        confidence = 0.0

        if len(results) > 0 and results[0].probs is not None:
            probs = results[0].probs
            class_id = int(probs.top1)
            raw_class_name = results[0].names[class_id]
            confidence = float(probs.top1conf.item())

            if raw_class_name == 'sitting_bad':
                raw_class = 'sitting_bad' if confidence >= 0.85 else 'sitting_good'
            elif raw_class_name == 'sitting_good':
                raw_class = 'sitting_good'
            else:
                raw_class = 'empty'

        # --- Debounce: confirm state after N consecutive stable frames ---
        if raw_class == st.session_state.pending_class:
            st.session_state.stable_frame_count += 1
        else:
            st.session_state.pending_class = raw_class
            st.session_state.stable_frame_count = 1

        if st.session_state.stable_frame_count >= DEBOUNCE_FRAMES:
            st.session_state.confirmed_class = st.session_state.pending_class

        confirmed = st.session_state.confirmed_class

        # --- Map confirmed state to serial command ---
        if confirmed == 'sitting_bad':
            serial_cmd = b'2'
        elif confirmed == 'sitting_good':
            serial_cmd = b'1'
        else:
            serial_cmd = b'0'

        # --- Send to YoloBit (rate-limited, only on change) ---
        if st.session_state.ser and st.session_state.ser.is_open:
            now = time.time()
            if serial_cmd != st.session_state.last_serial_cmd and \
               (now - st.session_state.last_serial_time) >= SERIAL_MIN_INTERVAL:
                try:
                    st.session_state.ser.write(serial_cmd)
                    st.session_state.last_serial_cmd = serial_cmd
                    st.session_state.last_serial_time = now
                except Exception:
                    pass

        # --- Drawing on frame ---
        if confirmed != 'empty':
            border_color = (0, 0, 255) if confirmed == 'sitting_bad' else (0, 255, 0)
            cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), border_color, 15)

            box_height = 80 if show_confidence else 55
            cv2.rectangle(frame, (10, 10), (380, box_height), border_color, -1)

            display_status = confirmed.replace("_", " ").upper()
            cv2.putText(frame, f"STATUS: {display_status}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

            if show_confidence:
                cv2.putText(frame, f"CONF: {confidence*100:.1f}%", (20, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

        # --- Status & Alerts ---
        if confirmed == 'sitting_bad':
            status_placeholder.metric("📊 Status", "BAD")
            alert_placeholder.error("⚠️ **WARNING:** POOR POSTURE DETECTED! Please sit up straight.")
        elif confirmed == 'sitting_good':
            status_placeholder.metric("📊 Status", "GOOD")
            alert_placeholder.success("✅ **GOOD:** Posture is correct. Keep it up!")
        else:
            status_placeholder.metric("📊 Status", "IDLE")
            alert_placeholder.empty()

        # --- Publish to Adafruit IO (rate-limited) ---
        now_aio = time.time()
        if (now_aio - st.session_state.last_aio_publish) >= AIO_PUBLISH_INTERVAL:
            posture_str = {"sitting_bad": "2", "sitting_good": "1"}.get(confirmed, "0")
            light_raw = st.session_state.light_value.replace("%", "").strip()
            ambient_raw = st.session_state.ambient_value.replace("%", "").strip()
            publish_all_feeds(posture_str, light_raw, ambient_raw)
            st.session_state.last_aio_publish = now_aio

    if cap is not None:
        cap.release()
else:
    frame_placeholder.info("⏸️ Camera is currently stopped. Click 'Start' in the sidebar to begin monitoring.")
