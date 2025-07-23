@echo off
echo Starting ComplaintHub Servers (Node.js Backend + React Frontend)...
echo.

echo Starting Node.js Backend Server on port 8001...
cd backend-nodejs
start "Backend Server" cmd /k "node server.js"
cd ..

echo.
echo Starting React Frontend Server on port 5173...
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