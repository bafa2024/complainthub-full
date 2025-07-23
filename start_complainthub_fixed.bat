@echo off
echo Starting ComplaintHub Application...
echo.

echo Starting Backend Server (Port 8002)...
start "Backend Server" cmd /k "cd /d %~dp0backend && python working_server.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo Starting Frontend Server (Port 5173)...
start "Frontend Server" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ComplaintHub Application Started!
echo Backend: http://localhost:8002
echo Frontend: http://localhost:5173
echo.
echo Press any key to close this window...
pause > nul