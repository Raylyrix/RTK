import os
from pathlib import Path

# Application Settings
APP_NAME = "AutoMailer Pro"
APP_VERSION = "1.2.0"

# File Paths
BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"
TEMPLATES_DIR = BASE_DIR / "templates"
LOGS_DIR = BASE_DIR / "logs"

# Google API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.settings.basic'  # For signature access
]

# Email Settings
DEFAULT_BATCH_SIZE = 50
DEFAULT_TIME_GAP = 5  # seconds between emails
MAX_RETRIES = 3
MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024  # 25MB Gmail limit

# GUI Settings
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 800
THEME = "equilux"  # Modern dark theme

# Create necessary directories
TEMPLATES_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True) 