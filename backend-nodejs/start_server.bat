@echo off
echo Starting ComplaintHub Node.js Backend...
echo.

cd /d "%~dp0"

echo Installing dependencies...
npm install

echo.
echo Starting server on port 8001...
echo.
npm run dev

pause 