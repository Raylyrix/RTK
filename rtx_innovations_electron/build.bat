@echo off
echo Building RTX Innovations Electron App...
echo.

echo Installing dependencies...
call npm install

echo.
echo Building webpack bundle...
call npm run build

echo.
echo Building Electron app...
call npm run build-win

echo.
echo Build completed successfully!
echo Check the dist-builds folder for the executable.
pause 