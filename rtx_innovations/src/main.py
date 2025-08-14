"""
RTX Innovations - Professional Email Marketing Platform
Main Application Entry Point
"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

# Import configuration
from config import create_directories, APP_NAME, APP_VERSION

def main():
    """Main application entry point"""
    try:
        # Initialize directories
        print("🚀 Initializing RTX Innovations...")
        create_directories()
        
        # Import and run main application
        from rtx_app import RTXInnovationsApp
        
        print(f"✅ {APP_NAME} v{APP_VERSION} initialized successfully!")
        
        # Create and run application
        app = RTXInnovationsApp()
        app.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 