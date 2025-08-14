"""
RTX Innovations - Build Script
Creates standalone executable for distribution
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess

def build_executable():
    """Build the RTX Innovations executable"""
    print("🚀 Building RTX Innovations Executable...")
    
    # Get project root
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    build_dir = project_root / "build"
    
    # Ensure build directory exists
    build_dir.mkdir(exist_ok=True)
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable
        "--windowed",  # No console window
        "--name=RTX_Innovations",
        f"--distpath={build_dir}",
        f"--workpath={build_dir / 'work'}",
        f"--specpath={build_dir}",
        "--add-data", f"{src_dir};src",  # Include source files
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "customtkinter",
        "--hidden-import", "ttkthemes",
        "--hidden-import", "pandas",
        "--hidden-import", "google.auth",
        "--hidden-import", "googleapiclient",
        "--hidden-import", "gspread",
        "--icon", str(project_root / "assets" / "icon.ico") if (project_root / "assets" / "icon.ico").exists() else "NONE",
        str(src_dir / "main.py")
    ]
    
    try:
        print("📦 Running PyInstaller...")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            
            # Copy additional files
            copy_additional_files(project_root, build_dir)
            
            # Create distribution package
            create_distribution_package(project_root, build_dir)
            
            print(f"🎉 Executable created in: {build_dir}")
            print("📁 You can now distribute RTX_Innovations.exe to other users!")
            
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except FileNotFoundError:
        print("❌ PyInstaller not found!")
        print("Please install it with: pip install pyinstaller")
    except Exception as e:
        print(f"❌ Build error: {e}")

def copy_additional_files(project_root: Path, build_dir: Path):
    """Copy additional required files"""
    print("📋 Copying additional files...")
    
    # Files to copy
    files_to_copy = [
        "README.md",
        "requirements.txt",
        "setup_guide.md"
    ]
    
    for file_name in files_to_copy:
        src_file = project_root / file_name
        dst_file = build_dir / file_name
        
        if src_file.exists():
            shutil.copy2(src_file, dst_file)
            print(f"✅ Copied: {file_name}")
    
    # Create assets directory
    assets_dir = build_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Copy assets if they exist
    src_assets = project_root / "assets"
    if src_assets.exists():
        for asset_file in src_assets.glob("*"):
            if asset_file.is_file():
                shutil.copy2(asset_file, assets_dir / asset_file.name)
                print(f"✅ Copied asset: {asset_file.name}")

def create_distribution_package(project_root: Path, build_dir: Path):
    """Create a complete distribution package"""
    print("📦 Creating distribution package...")
    
    # Create distribution directory
    dist_dir = build_dir / "RTX_Innovations_Distribution"
    dist_dir.mkdir(exist_ok=True)
    
    # Copy executable
    exe_file = build_dir / "RTX_Innovations.exe"
    if exe_file.exists():
        shutil.copy2(exe_file, dist_dir / "RTX_Innovations.exe")
        print("✅ Copied executable")
    
    # Copy additional files
    additional_files = [
        "README.md",
        "requirements.txt",
        "setup_guide.md"
    ]
    
    for file_name in additional_files:
        src_file = build_dir / file_name
        if src_file.exists():
            shutil.copy2(src_file, dist_dir / file_name)
    
    # Copy assets directory
    src_assets = build_dir / "assets"
    if src_assets.exists():
        dst_assets = dist_dir / "assets"
        shutil.copytree(src_assets, dst_assets, dirs_exist_ok=True)
    
    # Create batch file for easy launch
    create_launch_script(dist_dir)
    
    # Create ZIP archive
    create_zip_archive(build_dir, dist_dir)
    
    print(f"📦 Distribution package created in: {dist_dir}")

def create_launch_script(dist_dir: Path):
    """Create a batch file for easy launching"""
    batch_content = """@echo off
echo Starting RTX Innovations...
echo.
echo If you encounter any issues:
echo 1. Make sure you have the Google API credentials file
echo 2. Check the setup_guide.md for configuration
echo 3. Ensure you have internet connection
echo.
pause
start RTX_Innovations.exe
"""
    
    batch_file = dist_dir / "Launch_RTX_Innovations.bat"
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    
    print("✅ Created launch script")

def create_zip_archive(build_dir: Path, dist_dir: Path):
    """Create a ZIP archive of the distribution"""
    try:
        import zipfile
        
        zip_path = build_dir / "RTX_Innovations_v2.0.0.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in dist_dir.rglob('*'):
                if file_path.is_file():
                    arc_name = file_path.relative_to(dist_dir)
                    zipf.write(file_path, arc_name)
        
        print(f"📦 Created ZIP archive: {zip_path}")
        
    except ImportError:
        print("⚠️ ZIP creation skipped (zipfile module not available)")
    except Exception as e:
        print(f"⚠️ ZIP creation failed: {e}")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "pyinstaller",
        "customtkinter",
        "pandas",
        "google-auth",
        "google-api-python-client"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies are available!")
    return True

def main():
    """Main build function"""
    print("=" * 60)
    print("🚀 RTX Innovations - Build Script")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Cannot proceed without required dependencies!")
        return
    
    print("\n" + "=" * 60)
    
    # Build executable
    build_executable()
    
    print("\n" + "=" * 60)
    print("🎉 Build process completed!")
    print("=" * 60)

if __name__ == "__main__":
    main() 