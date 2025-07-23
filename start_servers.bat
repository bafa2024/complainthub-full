@echo off
echo Starting ComplaintHub Servers...
echo.

echo Starting Backend Server on port 8001...
cd backend
start "Backend Server" cmd /k "python minimal_server.py"
cd ..

echo.
echo Starting Frontend Server on port 5173...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo Servers are starting...
echo Backend: http://localhost:8001
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit this window...
pause > nul 