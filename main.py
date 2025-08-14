#!/usr/bin/env python3
"""
AutoMailer Pro - Main Application Entry Point

An automatic email sender with Google Sheets integration, scheduling,
and batch processing capabilities.

Author: AI Assistant
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from main_gui import AutoMailerGUI
    
    def main():
        """Main application entry point"""
        print("Starting AutoMailer Pro...")
        
        # Create and run the GUI application
        app = AutoMailerGUI()
        app.run()
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please make sure all required packages are installed.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1) 