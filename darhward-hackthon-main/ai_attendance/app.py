"""
Flask Backend for AI Attendance System
Main application with all routes and business logic
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, Response
import database
import face_utils
import camera
import cv2
import numpy as np
from datetime import datetime
import csv
import io
import os

app = Flask(__name__)

# Initialize database
if os.path.exists(database.DB_PATH):
    # If DB exists, try to load training data
    print("🔄 Loading existing data...")
    faces, ids, names_map = database.get_all_training_data()
    face_utils.train_model(faces, ids, names_map)
else:
    database.init_db()

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/register')
def register_page():
    """Registration page"""
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_student():
    """Handle student registration"""
    try:
        name = request.form.get('name', '').strip()
        roll_number = request.form.get('roll_number', '').strip()
        
        if not name or not roll_number:
            return jsonify({'success': False, 'message': 'Name and roll number required'}), 400
        
        # Capture images
        cam = camera.Camera()
        images = cam.capture_images(num_images=30, delay=0.1)
        
        if len(images) < 10:
            return jsonify({'success': False, 'message': 'Failed to capture images'}), 400
        
        # Process images for training
        training_faces = []
        for img in images:
            face_roi = face_utils.get_face_for_registration(img)
            if face_roi is not None:
                training_faces.append(face_roi)
        
        if len(training_faces) < 5:
            return jsonify({'success': False, 'message': 'Could not detect face clearly'}), 400
        
        # Save to database
        success = database.add_student(name, roll_number, training_faces)
        
        if success:
            # Save one reference image to faces folder
            if training_faces:
                face_filename = f"faces/{name}_{roll_number}.jpg"
                cv2.imwrite(face_filename, training_faces[0])
            
            # Retrain model with new data
            faces, ids, names_map = database.get_all_training_data()
            face_utils.train_model(faces, ids, names_map)
            
            return jsonify({'success': True, 'message': f'Student {name} registered!'})
        else:
            return jsonify({'success': False, 'message': 'Student already exists'}), 400
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Global status for attendance
current_attendance_status = {
    'status': 'idle', # idle, recognizing, verifying, marked, already_marked
    'student': None,
    'timestamp': None,
    'message': 'Looking for face...'
}

def generate_frames():
    """Video streaming generator function"""
    global current_attendance_status
    
    cam = camera.Camera()
    if not cam.start():
        return
    
    # Reset status
    current_attendance_status = {
        'status': 'recognizing',
        'student': None,
        'timestamp': None,
        'message': 'Looking for face...'
    }
    
    # Import liveness here to avoid circular imports if any
    import liveness
    liveness_detector = liveness.liveness_detector
    
    # Recognition tracking variables
    last_recognized_name = None
    consecutive_recognitions = 0
    verification_started = False
    
    # Alert counters
    unknown_face_counter = 0
    UNKNOWN_THRESHOLD = 30  # Approx 5 seconds at 6 FPS
    
    try:
        while True:
            frame = cam.read_frame()
            if frame is None:
                break
            
            # Process frame for recognition
            processed_frame, name, confidence = face_utils.detect_and_draw_faces(frame)
            
            # Unauthorized Access Logic
            if name is None:
                unknown_face_counter += 1
                if unknown_face_counter >= UNKNOWN_THRESHOLD:
                    if unknown_face_counter == UNKNOWN_THRESHOLD: # Log once per incident
                        database.log_alert("Unauthorized Access", "Unknown face detected for >5 seconds")
                        current_attendance_status['message'] = "⚠️ Unauthorized Access Detected!"
                    
                    cv2.putText(processed_frame, "UNAUTHORIZED", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                unknown_face_counter = 0

            # Logic Flow:
            # 1. Recognize Face
            # 2. If stable -> Start Liveness Verification
            # 3. If Verified -> Mark Attendance
            
            if name and confidence > 40:
                # Check stability
                if name == last_recognized_name:
                    consecutive_recognitions += 1
                else:
                    consecutive_recognitions = 1
                    last_recognized_name = name
                    verification_started = False
                    liveness_detector.reset()
                
                # If stable, start verification
                if consecutive_recognitions >= 3:
                    current_attendance_status['student'] = name
                    current_attendance_status['status'] = 'verifying'
                    
                    # Extract face ROI for liveness check
                    face_roi = face_utils.get_face_for_registration(frame)
                    
                    if face_roi is not None:
                        # Run Liveness Check
                        msg, is_verified = liveness_detector.verify_liveness(face_roi)
                        current_attendance_status['message'] = msg
                        
                        # Draw status on frame
                        cv2.putText(processed_frame, msg, (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        
                        if is_verified:
                            # Check if sessions exist and if so, validate active session
                            all_sessions = database.get_all_sessions()
                            
                            if all_sessions:  # Only enforce session validation if sessions exist
                                active_session = database.get_active_session()
                                
                                if not active_session:
                                    current_attendance_status['status'] = 'session_ended'
                                    current_attendance_status['message'] = '❌ No active session! Attendance closed.'
                                    cv2.putText(processed_frame, "SESSION ENDED", (10, 90), 
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                else:
                                    # Mark Attendance
                                    student_id = None
                                    for id_, n in face_utils.face_system.names_map.items():
                                        if n == name:
                                            student_id = id_
                                            break
                                    
                                    if student_id:
                                        result = database.mark_attendance(student_id, name)
                                        
                                        if isinstance(result, tuple):
                                            success, timestamp = result
                                            current_attendance_status['status'] = 'marked'
                                            current_attendance_status['timestamp'] = timestamp
                                            current_attendance_status['message'] = 'Attendance Marked!'
                                            
                                            # Check for Late Arrival (after 9:30 AM)
                                            current_time = datetime.now().time()
                                            late_threshold = datetime.strptime("09:30", "%H:%M").time()
                                            if current_time > late_threshold:
                                                database.log_alert("Late Arrival", f"{name} arrived late at {timestamp}")
                                                
                                        else:
                                            current_attendance_status['status'] = 'already_marked'
                                            current_attendance_status['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                            current_attendance_status['message'] = 'Already Marked Today'
                            else:
                                # No sessions exist, allow attendance freely
                                student_id = None
                                for id_, n in face_utils.face_system.names_map.items():
                                    if n == name:
                                        student_id = id_
                                        break
                                
                                    if student_id:
                                        result = database.mark_attendance(student_id, name)
                                        
                                        if isinstance(result, tuple):
                                            success, timestamp = result
                                            current_attendance_status['status'] = 'marked'
                                            current_attendance_status['timestamp'] = timestamp
                                            current_attendance_status['message'] = 'Attendance Marked!'
                                            
                                            # Check for Late Arrival (after 9:30 AM)
                                            current_time = datetime.now().time()
                                            late_threshold = datetime.strptime("09:30", "%H:%M").time()
                                            if current_time > late_threshold:
                                                database.log_alert("Late Arrival", f"{name} arrived late at {timestamp}")
                                            
                                            # Check for low attendance and send email warning
                                            try:
                                                import email_service
                                                import email_config
                                                
                                                if email_config.is_configured():
                                                    percentage = database.get_student_attendance_percentage(student_id)
                                                    # Get roll number
                                                    students = database.get_all_students_info()
                                                    roll_number = next((s[2] for s in students if s[0] == student_id), "N/A")
                                                    
                                                    email_service.send_low_attendance_warning(student_id, name, roll_number, percentage)
                                            except Exception as e:
                                                print(f"Error checking low attendance: {e}")
                                                
                                        else:
                                            current_attendance_status['status'] = 'already_marked'
                                            current_attendance_status['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                            current_attendance_status['message'] = 'Already Marked Today'
                    else:
                         current_attendance_status['message'] = "Face too far / not clear"
                else:
                    current_attendance_status['message'] = f"Recognizing {name}..."
            else:
                consecutive_recognitions = 0
                current_attendance_status['student'] = None
                current_attendance_status['status'] = 'recognizing'
                if unknown_face_counter < UNKNOWN_THRESHOLD:
                    current_attendance_status['message'] = "Looking for face..."
                liveness_detector.reset()
            
            # Encode frame
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            # Keep streaming even after marked to show success message
            if current_attendance_status['status'] in ['marked', 'already_marked']:
                pass

    finally:
        cam.stop()

@app.route('/attendance')
def attendance_page():
    """Attendance page with video feed"""
    return render_template('attendance.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/attendance_status')
def attendance_status():
    """API to check attendance status"""
    return jsonify(current_attendance_status)

@app.route('/start-attendance')
def start_attendance():
    """Deprecated: Redirect to new attendance page"""
    return redirect(url_for('attendance_page'))

@app.route('/dashboard')
def dashboard():
    students_raw = database.get_all_students_info()
    records_raw = database.get_attendance_records()
    
    # Convert students to dictionaries
    students = [{'id': s[0], 'name': s[1], 'roll_number': s[2]} for s in students_raw]
    
    # Convert attendance records to dictionaries
    attendance_records = [
        {'id': r[0], 'name': r[1], 'roll_number': r[2], 'timestamp': r[3], 'status': r[4]}
        for r in records_raw
    ]
    
    # Get absent students for today
    today = datetime.now().strftime('%Y-%m-%d')
    absent_students_raw = database.get_absent_students(today)
    absent_today = [{'id': s[0], 'name': s[1]} for s in absent_students_raw]
    
    # Get daily summary for present count
    daily_summary = database.get_daily_summary(today)
    present_count = daily_summary['present']
    
    # Get low attendance students (< 75%)
    leaderboard = database.get_student_leaderboard()
    low_attendance_students = [s for s in leaderboard if s['percentage'] < 75]
    
    # Get recent alerts
    alerts = database.get_recent_alerts(limit=10)
    
    return render_template('dashboard.html', 
                         students=students, 
                         attendance_records=attendance_records,
                         absent_today=absent_today,
                         present_count=present_count,
                         low_attendance_students=low_attendance_students,
                         alerts=alerts,
                         today_date=today)

@app.route('/api/attendance')
def get_attendance():
    date_filter = request.args.get('date')
    records = database.get_attendance_records(date_filter)
    # Record structure: id, name, roll_number, timestamp, status
    formatted = [{
        'id': r[0], 
        'name': r[1], 
        'roll_number': r[2],
        'timestamp': r[3], 
        'status': r[4]
    } for r in records]
    return jsonify({'success': True, 'records': formatted})

@app.route('/export-csv')
def export_csv():
    try:
        date_filter = request.args.get('date')
        records = database.get_attendance_records(date_filter)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Updated headers
        writer.writerow(['ID', 'Name', 'Roll Number', 'Date', 'Time In', 'Status'])
        
        for r in records:
            # r: id, name, roll_number, timestamp, status
            dt = datetime.strptime(r[3], '%Y-%m-%d %H:%M:%S')
            date_str = dt.strftime('%Y-%m-%d')
            time_str = dt.strftime('%H:%M:%S')
            
            writer.writerow([r[0], r[1], r[2], date_str, time_str, r[4]])
            
        output.seek(0)
        filename = f'attendance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student_route(student_id):
    """Delete a student and retrain model"""
    try:
        success, message = database.delete_student(student_id)
        
        if success:
            # Retrain model to remove student's face data
            print("🔄 Retraining model after deletion...")
            faces, ids, names_map = database.get_all_training_data()
            if faces:
                face_utils.train_model(faces, ids, names_map)
            else:
                # If no students left, we might want to clear the trainer or handle it
                print("⚠️ No students left to train.")
                
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        print(f"❌ Error in delete route: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/sessions')
def sessions_page():
    """Sessions management page"""
    sessions = database.get_all_sessions()
    active_session = database.get_active_session()
    return render_template('sessions.html', sessions=sessions, active_session=active_session)

@app.route('/create_session', methods=['POST'])
def create_session_route():
    """Create a new session"""
    try:
        name = request.form.get('name')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        date = request.form.get('date')
        
        if not all([name, start_time, end_time, date]):
            return jsonify({'success': False, 'message': 'All fields required'}), 400
        
        success = database.create_session(name, start_time, end_time, date)
        
        if success:
            return jsonify({'success': True, 'message': 'Session created successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to create session'}), 500
            
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/toggle_session/<int:session_id>/<int:is_active>', methods=['POST'])
def toggle_session_route(session_id, is_active):
    """Toggle session active status"""
    try:
        success = database.toggle_session(session_id, is_active)
        
        if success:
            status = "activated" if is_active else "deactivated"
            return jsonify({'success': True, 'message': f'Session {status}'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update session'}), 500
            
    except Exception as e:
        print(f"❌ Error toggling session: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/settings')
def settings_page():
    """Email settings page"""
    import email_config
    config = email_config.get_config()
    return render_template('settings.html', config=config)

@app.route('/save_settings', methods=['POST'])
def save_settings():
    """Save email configuration"""
    try:
        import email_config
        data = request.get_json()
        
        if email_config.update_config(data):
            return jsonify({'success': True, 'message': 'Settings saved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save settings'}), 500
            
    except Exception as e:
        print(f"❌ Error saving settings: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/send_test_email', methods=['POST'])
def send_test_email_route():
    """Send a test email"""
    try:
        import email_service
        
        if email_service.send_test_email():
            return jsonify({'success': True, 'message': 'Test email sent successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send test email. Check your configuration.'}), 500
            
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/send_daily_report', methods=['POST'])
def send_daily_report_route():
    """Manually send daily report"""
    try:
        import email_service
        
        if email_service.send_daily_report():
            return jsonify({'success': True, 'message': 'Daily report sent successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send report. Check your configuration.'}), 500
            
    except Exception as e:
        print(f"❌ Error sending daily report: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/send_absence_notifications', methods=['POST'])
def send_absence_notifications_route():
    """Send absence notifications to students"""
    try:
        import email_service
        
        if email_service.send_absence_notifications():
            return jsonify({'success': True, 'message': 'Absence notifications sent successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send notifications. Check your configuration.'}), 500
            
    except Exception as e:
        print(f"❌ Error sending absence notifications: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/student/<int:student_id>')
def student_profile(student_id):
    """Student profile page with calendar"""
    try:
        # Get student info
        conn = sqlite3.connect(database.DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, roll_number, created_at FROM students WHERE id = ?', (student_id,))
        student_data = cursor.fetchone()
        
        if not student_data:
            return "Student not found", 404
            
        student = {
            'id': student_data[0],
            'name': student_data[1],
            'roll_number': student_data[2],
            'created_at': student_data[3]
        }
        
        # Get attendance stats
        percentage = database.get_student_attendance_percentage(student_id)
        
        # Get attendance dates for calendar
        cursor.execute('SELECT DISTINCT DATE(timestamp) FROM attendance WHERE student_id = ?', (student_id,))
        attendance_dates = [row[0] for row in cursor.fetchall()]
        
        # Get recent records
        cursor.execute('SELECT timestamp FROM attendance WHERE student_id = ? ORDER BY timestamp DESC LIMIT 5', (student_id,))
        recent_records = [{'timestamp': row[0]} for row in cursor.fetchall()]
        
        # Calculate totals
        days_present = len(attendance_dates)
        created_date = datetime.strptime(student['created_at'], '%Y-%m-%d %H:%M:%S').date()
        today = datetime.now().date()
        total_days = (today - created_date).days + 1
        
        conn.close()
        
        return render_template('student_profile.html', 
                             student=student,
                             percentage=percentage,
                             attendance_dates=attendance_dates,
                             recent_records=recent_records,
                             days_present=days_present,
                             total_days=total_days)
                             
    except Exception as e:
        print(f"❌ Error loading student profile: {e}")
        return str(e), 500

@app.route('/analytics')
def analytics_page():
    """Analytics and reporting page"""
    # Get all analytics data
    leaderboard = database.get_student_leaderboard()
    weekly_report = database.get_weekly_report()
    monthly_report = database.get_monthly_report()
    trends = database.get_attendance_trends(30)
    
    return render_template('analytics.html', 
                         leaderboard=leaderboard,
                         weekly_report=weekly_report,
                         monthly_report=monthly_report,
                         trends=trends)

if __name__ == '__main__':
    print("🎓 AI Attendance System Starting...")
    print("📍 Server running at: http://127.0.0.1:5001")
    app.run(debug=False, host='127.0.0.1', port=5001)
