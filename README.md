# 🖥️ AI Workspace Posture Monitor

A real-time, lightweight web application that detects and alerts users about their sitting posture using **YOLOv8 (Image Classification)** and **Streamlit**.

## 🌟 Key Features
* **Accurate 3-State Detection:**
  * `SITTING GOOD` (Green border & Success alert)
  * `SITTING BAD` (Red border & Warning alert)
  * `EMPTY` (No bounding boxes, no alerts—clean UI when you step away)
* **Smart Tolerance Logic:** The AI forgives minor slouching, only triggering a "Bad Posture" alert when its confidence exceeds **80%**, significantly reducing alert fatigue.
* **Modern Control Panel:** Toggle confidence scores and control the camera directly from the sidebar.

---

## ⚡ Quick Start (Installation & Run)

Follow these steps to get the app running on your local machine in under a minute.

### 🪟 For Windows Users
Open your Command Prompt or PowerShell, then copy and paste this entire block:

```cmd
git clone <your_github_repo_link_here>
cd AI-Posture-Monitor
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py

