# 🎓 AI-Based Attendance Monitoring System

A complete, robust, and easy-to-install face recognition attendance system built with Python, OpenCV, Flask, and Streamlit. Designed for Python 3.13 compatibility on Windows.

## 🌟 Key Features

### 📸 Core Functionality
- **Face Registration**: Capture and register student faces using your webcam (stores 50 samples per student).
- **AI Recognition**: Real-time face detection and recognition using OpenCV's **LBPH (Local Binary Patterns Histograms)** algorithm.
- **Auto Attendance**: Automatically marks attendance with a precise timestamp upon successful recognition.
- **Duplicate Prevention**: Ensures attendance is marked only once per student per day.

### 🛡️ Security & Anti-Spoofing
- **Liveness Detection**: Integrated "Challenge-Response" system requiring users to **blink** to prove they are real humans.
- **Spoof Protection**: Detects and rejects static photos or screens using eye aspect ratio (EAR) analysis.
- **Secure Storage**: Face images are stored locally for training; no sensitive biometric data is sent to the cloud.

### 📊 Dashboards & Analytics
- **Web Admin Dashboard**:
    - View all registered students.
    - View daily attendance records.
    - Filter records by date.
    - Export data to CSV.
- **Streamlit Analytics Dashboard (New!)**:
    - **Real-time Metrics**: Total students, present, absent, and late counts.
    - **Interactive Charts**: Daily arrival timeline and attendance distribution pie charts.
    - **Advanced Reporting**: Export detailed reports to **Excel**, **PDF**, and **CSV**.
    - **Auto-Refresh**: Updates every 5 seconds for live monitoring.

---

## 🛠️ Tech Stack

- **Language**: Python 3.8 - 3.13
- **Computer Vision**: OpenCV (cv2), MediaPipe (optional for future upgrades)
- **Web Framework**: Flask (Backend), Bootstrap 5 (Frontend)
- **Analytics**: Streamlit, Pandas, Matplotlib
- **Database**: SQLite
- **Export**: FPDF (PDF), OpenPyXL (Excel)

---

## � Project Structure

```
ai-attendance/
│── app.py                 # Main Flask application (Web Interface)
│── camera.py              # Webcam handling & frame processing
│── face_utils.py          # LBPH Face Recognition & Training logic
│── liveness.py            # Anti-spoofing (Blink Detection) logic
│── database.py            # SQLite database management
│── dashboard_streamlit.py # Streamlit Analytics Dashboard
│── run_dashboard.bat      # Shortcut to run Streamlit Dashboard
│── requirements.txt       # Project dependencies
│── static/                # CSS, JS, and images
│── templates/             # HTML templates (index, register, dashboard)
│── models/                # Database (students.db) & Trainer (trainer.yml)
│── faces/                 # Directory storing registered face images
└── README.md              # Documentation
```

---

## 🚀 Installation Guide

### Prerequisites
- Python 3.8 or newer (Fully compatible with **Python 3.13**)
- A webcam
- Windows, Linux, or macOS

### Step 1: Install Dependencies
Open your terminal/command prompt in the project folder and run:
```bash
pip install -r requirements.txt
```
*Note: This project uses `opencv-contrib-python` for the LBPH recognizer, avoiding complex `dlib` installation issues.*

### Step 2: Initialize Database
Create the database and required tables:
```bash
python database.py
```

---

## 🎮 Usage Guide

### 1. Start the Web Application
Run the main Flask app:
```bash
python app.py
```
Access the interface at: **http://127.0.0.1:5001**

### 2. Register a Student
1. Go to **"Register Student"**.
2. Enter Name and Roll Number.
3. Click **"Capture Photos"**.
4. Follow the on-screen instructions (look at the camera).
5. The system captures 50 images and automatically retrains the model.

### 3. Mark Attendance (with Liveness Check)
1. Go to **"Mark Attendance"**.
2. Allow camera access.
3. **Liveness Check**: The system will ask you to **"BLINK NOW"**.
4. Once liveness is confirmed, it recognizes your face.
5. **Success**: A modal confirms "Attendance Marked" with the time.

### 4. View Analytics Dashboard
To see detailed charts and export reports, run the Streamlit dashboard:
```bash
streamlit run dashboard_streamlit.py
```
*Or simply double-click the `run_dashboard.bat` file on Windows.*

---

## 🧠 How It Works

### Face Recognition (LBPH)
Unlike deep learning models that require heavy GPUs, this system uses **Local Binary Patterns Histograms (LBPH)**.
1. **Training**: It divides the face into small regions and computes binary patterns for each pixel based on its neighbors.
2. **Histograms**: It creates histograms for these regions and concatenates them into a single vector.
3. **Recognition**: It compares the histogram of a new face with stored histograms using the Chi-square distance. A lower distance means a better match.

### Anti-Spoofing (Blink Detection)
To prevent users from holding up a photo:
1. **Eye Detection**: Uses Haar Cascades to locate eyes within the detected face.
2. **Blink Analysis**: Monitors the eyes for a rapid closure and reopening (blink) within a short timeframe.
3. **Validation**: Attendance is only marked **after** a valid blink is detected.

---

## 🔧 Troubleshooting

### Camera Not Opening
- Ensure no other app (Zoom, Teams) is using the webcam.
- Try changing `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` in `camera.py`.

### "Face Not Detected" during Registration
- Ensure good lighting.
- Remove glasses if they cause heavy reflections.
- Move closer to the camera.

### Streamlit Dashboard Not Running
- Ensure you installed all requirements: `pip install -r requirements.txt`.
- Run explicitly with `python -m streamlit run dashboard_streamlit.py`.

---

## � Future Enhancements
- [ ] Email/SMS Notifications for absence.
- [ ] Multi-camera support for large classrooms.
- [ ] Cloud database integration (Firebase/PostgreSQL).
- [ ] Mobile App (Flutter/React Native).

---

## 📝 License
This project is open-source and available for educational purposes.

**Built with ❤️ by Antigravity**
