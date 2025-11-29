"""
Database module for AI Attendance System
Handles SQLite database operations for students and attendance records
"""

import sqlite3
import pickle
from datetime import datetime, timedelta
import os
import cv2
import numpy as np

DB_PATH = os.path.join('models', 'students.db')

def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            roll_number TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table to store training images
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            image BLOB NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')
    
    # Attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Present',
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            date TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

def add_student(name, roll_number, face_images):
    """Add a new student with face images"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO students (name, roll_number)
            VALUES (?, ?)
        ''', (name, roll_number))
        
        student_id = cursor.lastrowid
        
        for img in face_images:
            _, img_encoded = cv2.imencode('.jpg', img)
            img_blob = img_encoded.tobytes()
            
            cursor.execute('''
                INSERT INTO face_images (student_id, image)
                VALUES (?, ?)
            ''', (student_id, img_blob))
        
        conn.commit()
        conn.close()
        print(f"✅ Student {name} registered successfully")
        return True
    except sqlite3.IntegrityError:
        print(f"❌ Student {name} already exists")
        return False
    except Exception as e:
        print(f"❌ Error adding student: {e}")
        return False

def get_all_training_data():
    """Retrieve all face images and labels for training"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name FROM students')
        students = cursor.fetchall()
        names_dict = {s[0]: s[1] for s in students}
        
        cursor.execute('SELECT student_id, image FROM face_images')
        records = cursor.fetchall()
        
        faces = []
        ids = []
        
        for student_id, img_blob in records:
            nparr = np.frombuffer(img_blob, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            
            if img is not None:
                faces.append(img)
                ids.append(student_id)
        
        conn.close()
        return faces, ids, names_dict
    except Exception as e:
        print(f"❌ Error fetching training data: {e}")
        return [], [], {}

def mark_attendance(student_id, name):
    """Mark attendance for a student"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        cursor.execute('''
            SELECT * FROM attendance 
            WHERE student_id = ? AND DATE(timestamp) = ?
        ''', (student_id, today))
        
        if cursor.fetchone():
            conn.close()
            print(f"⚠️ Attendance already marked for {name} today")
            return False
        
        now = datetime.now()
        timestamp_str = now.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO attendance (student_id, name, timestamp, status)
            VALUES (?, ?, ?, 'Present')
        ''', (student_id, name, timestamp_str))
        
        conn.commit()
        conn.close()
        print(f"✅ Attendance marked for {name} at {timestamp_str}")
        return True, timestamp_str
    except Exception as e:
        print(f"❌ Error marking attendance: {e}")
        return False

def get_attendance_records(date_filter=None):
    """Get attendance records with student details"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if date_filter:
            cursor.execute('''
                SELECT a.id, a.name, s.roll_number, a.timestamp, a.status 
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                WHERE DATE(a.timestamp) = ?
                ORDER BY a.timestamp DESC
            ''', (date_filter,))
        else:
            cursor.execute('''
                SELECT a.id, a.name, s.roll_number, a.timestamp, a.status 
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                ORDER BY a.timestamp DESC
            ''')
        
        records = cursor.fetchall()
        conn.close()
        return records
    except Exception as e:
        print(f"❌ Error fetching attendance: {e}")
        return []

def get_absent_students(date_str):
    """Get list of students who were absent on a specific date"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, roll_number FROM students')
        all_students = cursor.fetchall()
        
        cursor.execute('''
            SELECT DISTINCT student_id 
            FROM attendance 
            WHERE DATE(timestamp) = ?
        ''', (date_str,))
        attended_ids = {row[0] for row in cursor.fetchall()}
        
        absent = [s for s in all_students if s[0] not in attended_ids]
        
        conn.close()
        return absent
    except Exception as e:
        print(f"❌ Error getting absent students: {e}")
        return []

def get_all_students_info():
    """Get all students information"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, roll_number FROM students ORDER BY name')
        students = cursor.fetchall()
        
        conn.close()
        return students
    except Exception as e:
        print(f"❌ Error fetching students: {e}")
        return []

def log_alert(alert_type, message):
    """Log an alert to the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('INSERT INTO alerts (type, message) VALUES (?, ?)', (alert_type, message))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error logging alert: {e}")
        return False

def get_recent_alerts(limit=10):
    """Get recent alerts"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('SELECT type, message, timestamp FROM alerts ORDER BY timestamp DESC LIMIT ?', (limit,))
        alerts = cursor.fetchall()
        conn.close()
        return alerts
    except Exception as e:
        print(f"❌ Error fetching alerts: {e}")
        return []

def create_session(name, start_time, end_time, date):
    """Create a new session/class"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (name, start_time, end_time, date, is_active)
            VALUES (?, ?, ?, ?, 1)
        ''', (name, start_time, end_time, date))
        
        conn.commit()
        conn.close()
        print(f"✅ Session '{name}' created for {date} ({start_time} - {end_time})")
        return True
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        return False

def get_active_session():
    """Get currently active session based on current time"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M')
        
        cursor.execute('''
            SELECT id, name, start_time, end_time, date 
            FROM sessions 
            WHERE date = ? AND start_time <= ? AND end_time >= ? AND is_active = 1
            ORDER BY start_time DESC
            LIMIT 1
        ''', (current_date, current_time, current_time))
        
        session = cursor.fetchone()
        conn.close()
        return session
    except Exception as e:
        print(f"❌ Error getting active session: {e}")
        return None

def get_all_sessions():
    """Get all sessions"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, start_time, end_time, date, is_active 
            FROM sessions 
            ORDER BY date DESC, start_time DESC
        ''')
        
        sessions = cursor.fetchall()
        conn.close()
        return sessions
    except Exception as e:
        print(f"❌ Error fetching sessions: {e}")
        return []

def toggle_session(session_id, is_active):
    """Activate or deactivate a session"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE sessions SET is_active = ? WHERE id = ?', (is_active, session_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error toggling session: {e}")
        return False

def get_student_attendance_percentage(student_id):
    """Calculate attendance percentage for a student"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT created_at FROM students WHERE id = ?', (student_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return 0
        
        created_date = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S').date()
        today = datetime.now().date()
        total_days = (today - created_date).days + 1
        
        cursor.execute('SELECT COUNT(DISTINCT DATE(timestamp)) FROM attendance WHERE student_id = ?', (student_id,))
        attended_days = cursor.fetchone()[0]
        
        conn.close()
        
        if total_days == 0:
            return 0
        
        percentage = (attended_days / total_days) * 100
        return round(percentage, 2)
        
    except Exception as e:
        print(f"❌ Error calculating attendance percentage: {e}")
        return 0

def get_daily_summary(date_str):
    """Get summary of attendance for a specific date"""
    try:
        total_students = len(get_all_students_info())
        present_students = len(get_attendance_records(date_str))
        absent_students = len(get_absent_students(date_str))
        
        return {
            'total': total_students,
            'present': present_students,
            'absent': absent_students,
            'percentage': (present_students / total_students * 100) if total_students > 0 else 0
        }
    except Exception as e:
        print(f"❌ Error getting daily summary: {e}")
        return {'total': 0, 'present': 0, 'absent': 0, 'percentage': 0}

def get_weekly_report():
    """Get attendance report for the current week"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        
        weekly_data = []
        for i in range(7):
            date = start_of_week + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            day_name = date.strftime('%A')
            
            cursor.execute('SELECT COUNT(*) FROM attendance WHERE DATE(timestamp) = ?', (date_str,))
            count = cursor.fetchone()[0]
            
            weekly_data.append({
                'date': date_str,
                'day': day_name,
                'count': count
            })
        
        conn.close()
        return weekly_data
    except Exception as e:
        print(f"❌ Error getting weekly report: {e}")
        return []

def get_monthly_report():
    """Get attendance report for the current month"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        today = datetime.now()
        start_of_month = today.replace(day=1)
        start_date = start_of_month.strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM attendance
            WHERE DATE(timestamp) >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (start_date,))
        
        monthly_data = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        return monthly_data
    except Exception as e:
        print(f"❌ Error getting monthly report: {e}")
        return []

def get_student_leaderboard():
    """Get leaderboard of students by attendance percentage"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, roll_number, created_at FROM students')
        students = cursor.fetchall()
        
        leaderboard = []
        for student_id, name, roll_number, created_at in students:
            percentage = get_student_attendance_percentage(student_id)
            
            cursor.execute('SELECT COUNT(DISTINCT DATE(timestamp)) FROM attendance WHERE student_id = ?', (student_id,))
            days_attended = cursor.fetchone()[0]
            
            created_date = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').date()
            today = datetime.now().date()
            total_days = (today - created_date).days + 1
            
            leaderboard.append({
                'id': student_id,
                'name': name,
                'roll_number': roll_number,
                'percentage': percentage,
                'days_attended': days_attended,
                'total_days': total_days
            })
        
        leaderboard.sort(key=lambda x: x['percentage'], reverse=True)
        
        conn.close()
        return leaderboard
    except Exception as e:
        print(f"❌ Error getting leaderboard: {e}")
        return []

def get_attendance_trends(days=30):
    """Get attendance trends for the past N days"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        trends = []
        for i in range(days, 0, -1):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            cursor.execute('SELECT COUNT(*) FROM attendance WHERE DATE(timestamp) = ?', (date_str,))
            count = cursor.fetchone()[0]
            
            trends.append({
                'date': date_str,
                'count': count
            })
        
        conn.close()
        return trends
    except Exception as e:
        print(f"❌ Error getting attendance trends: {e}")
        return []

if __name__ == "__main__":
    init_db()
