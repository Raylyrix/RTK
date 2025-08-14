@echo off
echo Testing RTX Innovations Development Environment...
echo.

echo 1. Checking Node.js and npm...
node --version
npm --version

echo.
echo 2. Installing dependencies...
call npm install

echo.
echo 3. Building webpack bundle...
call npm run build

echo.
echo 4. Checking build output...
if exist "dist\bundle.js" (
    echo ✓ Bundle created successfully
) else (
    echo ✗ Bundle creation failed
    exit /b 1
)

if exist "dist\index.html" (
    echo ✓ HTML file created successfully
) else (
    echo ✗ HTML file creation failed
    exit /b 1
)

echo.
echo 5. Starting development server...
echo Starting in background... Check if Electron app opens.
call npm run dev

echo.
echo Development environment test completed!
pause 