@echo off
echo Starting RTX Innovations in Development Mode...
echo.

echo Installing dependencies if needed...
call npm install

echo.
echo Building and starting the app...
call npm run dev-simple

pause 