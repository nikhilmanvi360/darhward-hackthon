# 🎓 AI-Based Attendance Monitoring System

> Intelligent face-recognition attendance system with blink-based liveness detection, real-time analytics, and a modern web dashboard.

![Python](https://img.shields.io/badge/Python-3.8--3.13-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)
![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?logo=sqlite)

---

## 📖 Overview

This project is a complete AI-powered attendance management solution that combines **OpenCV LBPH face recognition**, **blink-based liveness detection**, **Flask**, **SQLite**, and **Streamlit analytics** to provide secure, automated attendance.

Unlike traditional attendance systems, this application verifies that a real person is standing in front of the camera before marking attendance.

---

## ✨ Features

- Face Registration (50 samples)
- Real-time Face Recognition (LBPH)
- Blink-based Anti-Spoofing
- Automatic Attendance
- Duplicate Prevention
- Flask Admin Dashboard
- Streamlit Analytics Dashboard
- CSV / Excel / PDF Export
- SQLite Database
- Python 3.13 Compatible

---

## 🖼 Screenshots

Create a `screenshots/` folder.

```text
screenshots/
├── home.png
├── register.png
├── attendance.png
├── dashboard.png
└── analytics.png
```

Example:

```md
![Home](screenshots/home.png)
```

---

## 🏗 System Architecture

```text
Webcam
   │
OpenCV Face Detection
   │
Blink Detection
   │
LBPH Recognition
   │
SQLite Database
   │
Flask Dashboard
   │
Streamlit Analytics
```

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| CV | OpenCV |
| Backend | Flask |
| Analytics | Streamlit |
| Database | SQLite |
| Reports | Pandas, OpenPyXL, FPDF |

---

## 📂 Project Structure

```text
app.py
camera.py
database.py
face_utils.py
liveness.py
dashboard_streamlit.py
templates/
static/
models/
faces/
requirements.txt
README.md
```

---

## 🚀 Installation

```bash
git clone <your-repository-url>
cd ai-attendance
pip install -r requirements.txt
python database.py
python app.py
```

Open:

http://127.0.0.1:5001

Analytics:

```bash
streamlit run dashboard_streamlit.py
```

---

## 🧠 How It Works

### Face Registration

Captures multiple face samples and trains an LBPH model.

### Face Recognition

LBPH compares histogram features of the live image against trained samples.

### Liveness Detection

The user must blink. Static photos cannot satisfy the blink challenge.

### Attendance

Once verified, attendance is recorded with timestamp while preventing duplicate entries.

---

## 📊 Dashboard

The Streamlit dashboard includes:

- Present/Absent metrics
- Daily attendance trends
- Pie charts
- Export to CSV
- Export to Excel
- Export to PDF

---

## 🔒 Security

- Blink verification
- Duplicate prevention
- Local data storage
- No cloud biometric upload

---

## 🔧 Troubleshooting

- Ensure webcam permissions are enabled.
- Close Zoom/Teams if camera is busy.
- Install all dependencies from `requirements.txt`.

---

## 🚀 Future Roadmap

- Email notifications
- Mobile application
- Multi-camera support
- PostgreSQL/Firebase
- Deep-learning face recognition

---

## 🤝 Contributing

Fork the repository, create a feature branch, commit your changes, and open a Pull Request.

---

## 📄 License

Open-source for educational purposes.

---

<p align="center">
Made with ❤️ by Nikhil Manvi(HANDAY}
</p>
