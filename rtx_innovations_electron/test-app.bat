@echo off
echo Testing RTX Innovations App...
echo.

echo 1. Building the app...
call npm run build

echo.
echo 2. Starting the app...
echo The app should open with a beautiful UI.
echo If you see a blank screen, check the console (F12) for errors.
echo.

call npm run dev-simple

pause 