#!/usr/bin/env python3
"""
Python Environment Diagnostic Script
This script helps identify issues with Python packages and environment
"""

import sys
import os
import subprocess

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1

def main():
    print("🔍 Python Environment Diagnostic")
    print("=" * 50)
    
    # Python version and location
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Path: {sys.path[0]}")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print(f"In Virtual Environment: {in_venv}")
    
    # Check pip
    print("\n📦 Pip Information:")
    pip_stdout, pip_stderr, pip_code = run_command(f'"{sys.executable}" -m pip --version')
    if pip_code == 0:
        print(f"Pip: {pip_stdout.strip()}")
    else:
        print(f"Pip Error: {pip_stderr}")
    
    # Check if customtkinter is installed
    print("\n🔍 Checking customtkinter installation:")
    try:
        import customtkinter
        print(f"✅ customtkinter is available: {customtkinter.__version__}")
    except ImportError as e:
        print(f"❌ customtkinter import failed: {e}")
        
        # Try to install it
        print("\n🚀 Attempting to install customtkinter...")
        install_stdout, install_stderr, install_code = run_command(f'"{sys.executable}" -m pip install customtkinter')
        
        if install_code == 0:
            print("✅ Installation successful!")
            try:
                import customtkinter
                print(f"✅ customtkinter now available: {customtkinter.__version__}")
            except ImportError:
                print("❌ Still can't import after installation")
        else:
            print(f"❌ Installation failed: {install_stderr}")
    
    # Check other key packages
    print("\n📋 Checking other key packages:")
    packages = ['tkinter', 'pandas', 'google.auth', 'gspread']
    
    for package in packages:
        try:
            if package == 'tkinter':
                import tkinter
                print(f"✅ {package}: Available")
            elif package == 'pandas':
                import pandas
                print(f"✅ {package}: {pandas.__version__}")
            elif package == 'google.auth':
                import google.auth
                print(f"✅ {package}: Available")
            elif package == 'gspread':
                import gspread
                print(f"✅ {package}: {gspread.__version__}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
    
    # Check sys.path for package locations
    print("\n🗂️ Python package search paths:")
    for i, path in enumerate(sys.path[:5]):  # Show first 5 paths
        print(f"  {i+1}: {path}")
    
    if len(sys.path) > 5:
        print(f"  ... and {len(sys.path) - 5} more paths")

if __name__ == "__main__":
    main() 