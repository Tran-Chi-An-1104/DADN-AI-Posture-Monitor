import cv2
import streamlit as st
from ultralytics import YOLO
import serial

# ==========================================
# 1. PAGE CONFIGURATION & SESSION STATE
# ==========================================
st.set_page_config(
    page_title="AI Posture Monitor",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Khởi tạo các biến trạng thái
if "camera_running" not in st.session_state:
    st.session_state.camera_running = False
if "ser" not in st.session_state:
    st.session_state.ser = None

# ==========================================
# 2. MODEL LOADING
# ==========================================
@st.cache_resource(show_spinner="Loading AI Model...")
def load_model():
    """Loads the YOLO classification model and caches it."""
    return YOLO("best.pt") 

model = load_model()

# ==========================================
# 3. SIDEBAR: CONTROLS & SETTINGS
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
    st.subheader("🔌 Hardware Connection")
    # Ô nhập cổng USB kết nối với mạch (VD: COM3, COM4...)
    com_port = st.text_input("COM Port", placeholder="e.g., COM3")

    if st.button("Connect Hardware", use_container_width=True):
        try:
            # Mở cổng Serial với tốc độ 115200
            st.session_state.ser = serial.Serial(com_port, 115200, timeout=1)
            st.sidebar.success(f"✅ Connected to {com_port}")
        except Exception as e:
            st.sidebar.error("❌ Connection failed! Check COM port.")

    st.markdown("---")
    st.info("💡 **Note:** The system uses an 85% confidence tolerance. Mild slouching might be forgiven to prevent alert fatigue.")

# ==========================================
# 4. MAIN DASHBOARD AREA
# ==========================================
st.title("🖥️ AI Workspace Posture Monitor")
st.markdown("Real-time classification system analyzing your sitting posture.")

alert_placeholder = st.empty()
frame_placeholder = st.empty()

# ==========================================
# 5. CAMERA PROCESSING LOOP
# ==========================================
if st.session_state.camera_running:
    cap = cv2.VideoCapture(0) # Mở webcam
    
    # Ép camera hiển thị góc rộng HD (Tránh bị zoom cận mặt)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        st.error("❌ Error: Could not access the webcam. Please check your device permissions.")
        st.session_state.camera_running = False
    
    while st.session_state.camera_running:
        success, frame = cap.read()
        if not success:
            alert_placeholder.error("❌ Error: Failed to read frame from webcam.")
            break
            
        # Run AI Inference
        results = model.predict(frame, verbose=False)
        
        final_class = "empty"
        confidence = 0.0
        border_color = None
        
        # --- PREDICTION & TOLERANCE LOGIC ---
        if len(results) > 0 and results[0].probs is not None:
            probs = results[0].probs
            class_id = int(probs.top1)
            raw_class_name = results[0].names[class_id] 
            confidence = float(probs.top1conf.item())
            
            if raw_class_name == 'sitting_bad':
                if confidence >= 0.85: 
                    final_class = 'sitting_bad'
                    border_color = (0, 0, 255) # Đỏ
                else:
                    final_class = 'sitting_good' 
                    border_color = (0, 255, 0) # Xanh lá
                    
            elif raw_class_name == 'sitting_good':
                final_class = 'sitting_good'
                border_color = (0, 255, 0) # Xanh lá
                
            else:
                final_class = 'empty'

        # ==========================================
        # 6. GỬI TÍN HIỆU XUỐNG MẠCH PHẦN CỨNG
        # ==========================================
        if st.session_state.ser and st.session_state.ser.is_open:
            try:
                if final_class == 'sitting_bad':
                    st.session_state.ser.write(b'1') # Bật còi
                elif final_class == 'sitting_good':
                    st.session_state.ser.write(b'0') # Tắt còi
                else:
                    st.session_state.ser.write(b'2') # Trạng thái rỗng
            except Exception as e:
                pass # Bỏ qua lỗi nếu lỡ rút cáp đột ngột

        # --- DRAWING ON FRAME ---
        if final_class != 'empty':
            cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), border_color, 15)
            
            box_height = 80 if show_confidence else 55
            cv2.rectangle(frame, (10, 10), (380, box_height), border_color, -1)
            
            display_status = final_class.replace("_", " ").upper()
            cv2.putText(frame, f"STATUS: {display_status}", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            
            if show_confidence:
                cv2.putText(frame, f"CONF: {confidence*100:.1f}%", (20, 70), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        # Chuyển đổi màu hiển thị Web
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
        
        # Render Alerts
        if final_class == 'sitting_bad':
            alert_placeholder.error("⚠️ **WARNING:** POOR POSTURE DETECTED! Please sit up straight.")
        elif final_class == 'sitting_good':
            alert_placeholder.success("✅ **GOOD:** Posture is correct. Keep it up!")
        else:
            alert_placeholder.empty()
            
    if cap is not None:
        cap.release()
else:
    frame_placeholder.info("⏸️ Camera is currently stopped. Click 'Start' in the sidebar to begin monitoring.")