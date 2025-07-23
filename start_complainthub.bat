@echo off
title ComplaintHub - Full Stack Startup
color 0A

echo.
echo ========================================
echo    ComplaintHub - Full Stack Startup
echo ========================================
echo.

echo 🚀 Starting ComplaintHub application...
echo.

echo 📦 Step 1: Installing Node.js backend dependencies...
cd /d "%~dp0\backend-nodejs"
call npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)
echo ✅ Backend dependencies installed
echo.

echo 📦 Step 2: Installing React frontend dependencies...
cd /d "%~dp0\frontend"
call npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)
echo ✅ Frontend dependencies installed
echo.

echo 🔧 Step 3: Starting Node.js backend server...
cd /d "%~dp0\backend-nodejs"
start "ComplaintHub Backend" cmd /k "npm run dev"
echo ✅ Backend server starting on http://localhost:8001
echo.

echo ⏳ Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo 🔧 Step 4: Starting React frontend server...
cd /d "%~dp0\frontend"
start "ComplaintHub Frontend" cmd /k "npm run dev"
echo ✅ Frontend server starting on http://localhost:5173
echo.

echo ⏳ Waiting 3 seconds for frontend to start...
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo    🎉 ComplaintHub is starting up!
echo ========================================
echo.
echo 📊 Backend API:  http://localhost:8001
echo 🌐 Frontend App: http://localhost:5173
echo 📋 Health Check: http://localhost:8001/health
echo.
echo 💡 Both servers are running in separate windows.
echo 💡 Close those windows to stop the servers.
echo.
echo 🔍 Testing backend connection...
cd /d "%~dp0\backend-nodejs"
node test_backend.js
echo.

echo ✅ Setup complete! Your ComplaintHub application is ready.
echo.
pause 