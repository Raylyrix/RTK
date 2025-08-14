@echo off
echo 🚀 RTX Innovations - Setup Script
echo ===================================
echo.

echo 📦 Installing dependencies...
npm install

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully!
echo.

echo 🔧 Setting up development environment...
echo.

echo 🚀 Starting development server...
echo.
echo 📱 The application will open in a new window
echo 🔧 Developer tools will be available
echo 📝 Make changes to files and see them live!
echo.

npm run dev

pause 