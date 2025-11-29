"""
Email Configuration Module
Stores email settings for the notification system
"""

import os
import json

CONFIG_FILE = 'email_config.json'

# Default configuration
DEFAULT_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': '',
    'sender_password': '',
    'admin_email': '',
    'low_attendance_threshold': 75,
    'daily_report_time': '18:00',
    'notifications_enabled': False
}

def load_config():
    """Load email configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save email configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_config():
    """Get current configuration"""
    return load_config()

def update_config(updates):
    """Update configuration with new values"""
    config = load_config()
    config.update(updates)
    return save_config(config)

def is_configured():
    """Check if email is properly configured and enabled"""
    config = load_config()
    return (config.get('sender_email') and 
            config.get('sender_password') and 
            config.get('admin_email') and
            config.get('notifications_enabled'))

def has_credentials():
    """Check if email credentials are present (ignoring enabled status)"""
    config = load_config()
    return (config.get('sender_email') and 
            config.get('sender_password') and 
            config.get('admin_email'))
