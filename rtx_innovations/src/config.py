"""
RTX Innovations - Professional Email Marketing Platform
Enhanced Configuration and Settings
"""

import os
from pathlib import Path
from typing import Dict, Any

# Application Information
APP_NAME = "RTX Innovations"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Professional Email Marketing & Automation Platform"
APP_AUTHOR = "RTX Innovations Team"
APP_WEBSITE = "https://rtxinnovations.com"

# File Paths
BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
BUILD_DIR = BASE_DIR / "build"
TEMPLATES_DIR = BASE_DIR / "templates"
LOGS_DIR = BASE_DIR / "logs"
EXPORTS_DIR = BASE_DIR / "exports"
CACHE_DIR = BASE_DIR / "cache"

# Google API Configuration
GOOGLE_API_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/drive.file'
]

# Email Settings
EMAIL_CONFIG = {
    'default_batch_size': 25,
    'max_batch_size': 100,
    'default_time_gap': 3,  # seconds
    'max_time_gap': 60,
    'max_attachment_size': 25 * 1024 * 1024,  # 25MB
    'max_attachments_per_email': 10,
    'retry_attempts': 3,
    'retry_delay': 5,  # seconds
    'enable_tracking': True,
    'enable_analytics': True,
}

# UI Configuration
UI_CONFIG = {
    'theme': 'dark',  # dark, light, system
    'accent_color': '#007AFF',  # iOS Blue
    'success_color': '#34C759',  # iOS Green
    'warning_color': '#FF9500',  # iOS Orange
    'error_color': '#FF3B30',    # iOS Red
    'window_width': 1400,
    'window_height': 900,
    'min_width': 1200,
    'min_height': 800,
    'animation_duration': 300,  # milliseconds
    'tooltip_delay': 1000,      # milliseconds
    'enable_animations': True,
    'enable_shadows': True,
    'enable_gradients': True,
}

# Data Processing
DATA_CONFIG = {
    'max_preview_rows': 1000,
    'max_sheet_size': 10000,  # rows
    'auto_save_interval': 30,  # seconds
    'backup_interval': 300,    # seconds
    'export_formats': ['xlsx', 'csv', 'json'],
    'enable_real_time_updates': True,
    'enable_data_validation': True,
}

# Status Tracking
STATUS_COLUMNS = {
    'email_status': 'Email Status',
    'sent_date': 'Sent Date',
    'sent_time': 'Sent Time',
    'batch_id': 'Batch ID',
    'attempts': 'Attempts',
    'error_message': 'Error Message',
    'tracking_id': 'Tracking ID',
    'opened': 'Opened',
    'clicked': 'Clicked',
    'bounced': 'Bounced',
    'unsubscribed': 'Unsubscribed',
    'delivered': 'Delivered',
    'failed': 'Failed',
    'pending': 'Pending',
    'scheduled': 'Scheduled',
}

# Batch Management
BATCH_CONFIG = {
    'max_concurrent_batches': 5,
    'batch_naming': 'auto',  # auto, custom, timestamp
    'auto_retry_failed': True,
    'failed_email_threshold': 0.1,  # 10% failure rate
    'pause_on_threshold': True,
    'enable_batch_labels': True,
    'enable_batch_editing': True,
    'enable_batch_tracking': True,
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_rotation': 'daily',
    'max_log_files': 30,
    'log_to_file': True,
    'log_to_console': True,
    'enable_debug_logging': False,
}

# Security & Privacy
SECURITY_CONFIG = {
    'encrypt_credentials': True,
    'session_timeout': 3600,  # 1 hour
    'max_login_attempts': 5,
    'lockout_duration': 900,  # 15 minutes
    'require_2fa': False,
    'enable_audit_logging': True,
}

# Performance & Optimization
PERFORMANCE_CONFIG = {
    'enable_caching': True,
    'cache_ttl': 3600,  # 1 hour
    'max_threads': 10,
    'memory_limit': 512 * 1024 * 1024,  # 512MB
    'enable_compression': True,
    'enable_lazy_loading': True,
}

# Multi-Account Support
ACCOUNT_CONFIG = {
    'max_accounts': 10,
    'enable_account_switching': True,
    'enable_account_sharing': False,
    'enable_account_backup': True,
    'account_auto_save': True,
}

# Google Sheets Integration
SHEETS_CONFIG = {
    'enable_real_time_sync': True,
    'enable_auto_backup': True,
    'enable_status_updates': True,
    'enable_batch_editing': True,
    'enable_column_editing': True,
    'enable_row_editing': True,
    'enable_data_validation': True,
    'max_edit_operations': 1000,
}

# Email Campaign Features
CAMPAIGN_CONFIG = {
    'enable_templates': True,
    'enable_attachments': True,
    'enable_scheduling': True,
    'enable_tracking': True,
    'enable_analytics': True,
    'enable_a_b_testing': True,
    'enable_segmentation': True,
    'enable_automation': True,
}

# Analytics & Reporting
ANALYTICS_CONFIG = {
    'enable_real_time_tracking': True,
    'enable_custom_reports': True,
    'enable_data_export': True,
    'enable_charts': True,
    'enable_dashboards': True,
    'data_retention_days': 365,
}

# Create necessary directories
def create_directories():
    """Create all necessary directories"""
    directories = [
        TEMPLATES_DIR,
        LOGS_DIR,
        EXPORTS_DIR,
        CACHE_DIR,
        BUILD_DIR
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

# Initialize configuration
if __name__ == "__main__":
    create_directories()
    print(f"🚀 {APP_NAME} v{APP_VERSION} configuration initialized!") 