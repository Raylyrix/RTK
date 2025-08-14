#!/usr/bin/env python3
"""
AutoMailer Pro Installation Script

This script helps you set up AutoMailer Pro by:
1. Checking Python version
2. Installing required dependencies
3. Creating necessary directories
4. Providing setup instructions

Run this script before using AutoMailer Pro for the first time.
"""

import sys
import subprocess
import os
from pathlib import Path
import pkg_resources

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required.")
        print(f"Current version: Python {sys.version}")
        return False
    else:
        print(f"✅ Python version OK: {sys.version}")
        return True

def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling dependencies...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ Error: requirements.txt file not found!")
        return False
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    
    base_dir = Path(__file__).parent
    directories = [
        base_dir / "templates",
        base_dir / "logs"
    ]
    
    for directory in directories:
        try:
            directory.mkdir(exist_ok=True)
            print(f"✅ Created directory: {directory.name}")
        except Exception as e:
            print(f"❌ Error creating directory {directory.name}: {e}")
            return False
    
    return True

def check_credentials():
    """Check if credentials.json exists"""
    print("\nChecking Google API credentials...")
    
    credentials_file = Path(__file__).parent / "credentials.json"
    
    if credentials_file.exists():
        print("✅ credentials.json found!")
        return True
    else:
        print("⚠️  credentials.json NOT found!")
        print("\nTo use AutoMailer Pro, you need to:")
        print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
        print("2. Create a project and enable Gmail & Sheets APIs")
        print("3. Create OAuth 2.0 credentials for desktop application")
        print("4. Download the credentials JSON file")
        print("5. Rename it to 'credentials.json' and place it in this folder")
        print("\nSee setup_guide.md for detailed instructions.")
        return False

def verify_installation():
    """Verify that all packages are properly installed"""
    print("\nVerifying installation...")
    
    required_packages = [
        "google-auth-oauthlib",
        "google-auth-httplib2", 
        "google-api-python-client",
        "gspread",
        "oauth2client",
        "schedule",
        "python-dotenv",
        "email-validator",
        "pillow",
        "ttkthemes",
        "pandas",
        "openpyxl"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            pkg_resources.get_distribution(package)
            print(f"✅ {package}")
        except pkg_resources.DistributionNotFound:
            missing_packages.append(package)
            print(f"❌ {package} - NOT FOUND")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        return False
    else:
        print("\n✅ All packages verified!")
        return True

def main():
    """Main installation process"""
    print("=" * 50)
    print("AutoMailer Pro Installation Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Verify installation
    if not verify_installation():
        return False
    
    # Check credentials
    has_credentials = check_credentials()
    
    print("\n" + "=" * 50)
    print("Installation Summary")
    print("=" * 50)
    
    if has_credentials:
        print("🎉 Installation completed successfully!")
        print("\nYou can now run AutoMailer Pro:")
        print("   python main.py")
    else:
        print("✅ Base installation completed!")
        print("⚠️  Google API credentials still needed.")
        print("\nNext steps:")
        print("1. Set up Google API credentials (see setup_guide.md)")
        print("2. Run: python main.py")
    
    print("\nFor help and documentation:")
    print("- Read README.md for usage instructions")
    print("- Read setup_guide.md for Google API setup")
    print("- Check the application's Help menu")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Installation failed. Please check the errors above.")
            sys.exit(1)
        else:
            print("\n✅ Ready to use AutoMailer Pro!")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during installation: {e}")
        sys.exit(1) 