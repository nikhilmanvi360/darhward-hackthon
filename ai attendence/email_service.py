"""
Email Service Module
Handles sending email notifications for attendance system
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import email_config
import database

def send_email(to_email, subject, html_body):
    """
    Send an email using configured SMTP settings
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML content of email
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    config = email_config.get_config()
    
    if not email_config.is_configured():
        print("❌ Email not configured")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = config['sender_email']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach HTML body
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Connect to SMTP server
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['sender_email'], config['sender_password'])
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def generate_daily_report_html(date_str):
    """Generate HTML for daily attendance report"""
    students = database.get_all_students_info()
    present = database.get_attendance_records(date_str)
    absent = database.get_absent_students(date_str)
    
    total_students = len(students)
    total_present = len(present)
    total_absent = len(absent)
    attendance_rate = (total_present / total_students * 100) if total_students > 0 else 0
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #667eea; margin-bottom: 10px; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat {{ text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
            .stat-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
            .stat-label {{ color: #666; margin-top: 5px; }}
            .section {{ margin: 20px 0; }}
            .section-title {{ font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px; }}
            .student-list {{ background: #f8f9fa; padding: 15px; border-radius: 8px; }}
            .student-item {{ padding: 8px; border-bottom: 1px solid #ddd; }}
            .student-item:last-child {{ border-bottom: none; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Daily Attendance Report</h1>
            <p style="color: #666;">Date: {date_str}</p>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{total_students}</div>
                    <div class="stat-label">Total Students</div>
                </div>
                <div class="stat">
                    <div class="stat-value" style="color: #4facfe;">{total_present}</div>
                    <div class="stat-label">Present</div>
                </div>
                <div class="stat">
                    <div class="stat-value" style="color: #f5576c;">{total_absent}</div>
                    <div class="stat-label">Absent</div>
                </div>
                <div class="stat">
                    <div class="stat-value" style="color: #00f2fe;">{attendance_rate:.1f}%</div>
                    <div class="stat-label">Attendance Rate</div>
                </div>
            </div>
    """
    
    if absent:
        html += """
            <div class="section">
                <div class="section-title">❌ Absent Students</div>
                <div class="student-list">
        """
        for student in absent:
            html += f'<div class="student-item">{student[0]} - {student[1]}</div>'
        html += """
                </div>
            </div>
        """
    else:
        html += '<div class="section"><p style="color: #4facfe; font-weight: bold;">🎉 Perfect Attendance! Everyone was present today.</p></div>'
    
    html += """
            <div class="footer">
                <p>AI Attendance System - Automated Daily Report</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def generate_low_attendance_html(student_name, roll_number, percentage, threshold):
    """Generate HTML for low attendance warning"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            h1 {{ color: #f5576c; }}
            .student-info {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .percentage {{ font-size: 48px; font-weight: bold; color: #f5576c; text-align: center; margin: 20px 0; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚠️ Low Attendance Alert</h1>
            
            <div class="warning">
                <strong>Warning:</strong> A student's attendance has dropped below the threshold of {threshold}%
            </div>
            
            <div class="student-info">
                <p><strong>Student Name:</strong> {student_name}</p>
                <p><strong>Roll Number:</strong> {roll_number}</p>
            </div>
            
            <div class="percentage">{percentage:.1f}%</div>
            <p style="text-align: center; color: #666;">Current Attendance Percentage</p>
            
            <div class="footer">
                <p>AI Attendance System - Automated Alert</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_daily_report(date_str=None):
    """Send daily attendance report to admin"""
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    config = email_config.get_config()
    
    if not email_config.has_credentials():
        print("❌ Email credentials missing, skipping daily report")
        return False
    
    html = generate_daily_report_html(date_str)
    subject = f"Daily Attendance Report - {date_str}"
    
    return send_email(config['admin_email'], subject, html)

def send_low_attendance_warning(student_id, student_name, roll_number, percentage):
    """Send low attendance warning to admin"""
    config = email_config.get_config()
    
    if not email_config.is_configured():
        return False
    
    threshold = config['low_attendance_threshold']
    
    if percentage >= threshold:
        return False  # No warning needed
    
    html = generate_low_attendance_html(student_name, roll_number, percentage, threshold)
    subject = f"⚠️ Low Attendance Alert - {student_name}"
    
    return send_email(config['admin_email'], subject, html)

def send_test_email():
    """Send a test email to verify configuration"""
    config = email_config.get_config()
    
    if not email_config.has_credentials():
        return False
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #667eea; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ Test Email Successful!</h1>
            <p>Your email configuration is working correctly.</p>
            <p>You will now receive:</p>
            <ul>
                <li>Daily attendance reports</li>
                <li>Low attendance warnings</li>
                <li>System notifications</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return send_email(config['admin_email'], "Test Email - AI Attendance System", html)

def generate_absence_notification_html(student_name, date):
    """Generate HTML for student absence notification"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .content {{ padding: 20px; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; text-align: center; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 0;">📢 Absence Notification</h1>
            </div>
            <div class="content">
                <p>Dear {student_name},</p>
                
                <div class="warning">
                    <strong>⚠️ You were marked absent on {date}</strong>
                </div>
                
                <p>Our records show that you did not mark your attendance today. If this is an error or you have a valid reason for your absence, please contact your instructor.</p>
                
                <p><strong>Important:</strong> Regular attendance is crucial for your academic success. Please ensure you attend all scheduled sessions.</p>
                
                <p>If you have any questions or concerns, please don't hesitate to reach out.</p>
                
                <p>Best regards,<br>
                <strong>AI Attendance System</strong></p>
            </div>
            <div class="footer">
                <p>This is an automated message from the AI Attendance System</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def send_absence_notifications(date_str=None):
    """Send absence notifications to all absent students"""
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    if not email_config.is_configured():
        print("❌ Email not configured, skipping absence notifications")
        return False
    
    import database
    
    # Get absent students
    absent_students = database.get_absent_students(date_str)
    
    if not absent_students:
        print("✅ No absent students today")
        return True
    
    sent_count = 0
    for student_id, student_name, roll_number, email in absent_students:
        if email:  # Only send if email exists
            html = generate_absence_notification_html(student_name, date_str)
            subject = f"Absence Notification - {date_str}"
            
            if send_email(email, subject, html):
                sent_count += 1
                print(f"✅ Sent absence notification to {student_name} ({email})")
            else:
                print(f"❌ Failed to send to {student_name} ({email})")
        else:
            print(f"⚠️  No email for {student_name}, skipping")
    
    print(f"📧 Sent {sent_count} absence notifications")
    return True
