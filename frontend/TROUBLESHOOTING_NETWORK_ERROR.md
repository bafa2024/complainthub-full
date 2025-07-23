# Troubleshooting: "No response from server" Error

## 🚨 Problem Description
You're seeing the error: **"No response from server. Please check your network connection"**

## 🔍 Root Cause Analysis
This error occurs when the frontend tries to make API calls to the backend server, but the backend server is either:
1. Not running
2. Not accessible
3. Has import/module errors

## ✅ Quick Fixes

### Fix 1: Use Mockup Mode (Recommended)
The authentication system is configured to work in **mockup mode** without requiring a backend server.

**Steps:**
1. Open browser console (F12)
2. Check if you see: `🔧 Mockup mode enabled - using mock data`
3. If not, the mockup mode might be disabled

**Verify Mockup Mode:**
- Navigate to: http://localhost:5173/debug-auth
- Check if "Mockup Mode" shows as "✅ Enabled"
- If not, click "Toggle Mode" button

### Fix 2: Check Frontend Server
Ensure the frontend server is running:

```bash
cd frontend
npm run dev
```

**Expected Output:**
```
VITE v7.0.2  ready in 849 ms
➜  Local:   http://localhost:5173/
```

### Fix 3: Clear Browser Cache
Sometimes cached data can cause issues:

1. Open browser developer tools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"
4. Or use Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

## 🔧 Debug Steps

### Step 1: Check Console Logs
1. Open browser console (F12)
2. Look for these messages:
   - ✅ `🔧 Mockup mode enabled - using mock data`
   - ✅ `🔧 Mockup login with: test@example.com`
   - ❌ Any red error messages

### Step 2: Use Debug Panel
1. Navigate to: http://localhost:5173/debug-auth
2. Check the "Current Status" section
3. Run the test buttons
4. Review the debug information

### Step 3: Check Network Tab
1. Open browser developer tools (F12)
2. Go to "Network" tab
3. Try to login/signup
4. Look for failed API calls (red entries)

## 🎯 Testing Without Backend

### Test Login (Mockup Mode)
1. Go to: http://localhost:5173/login
2. Enter any email: `test@example.com`
3. Enter any password: `password123`
4. Click "Login"
5. Should redirect to dashboard

### Test Signup (Mockup Mode)
1. Go to: http://localhost:5173/signup
2. Fill all required fields
3. Click "Register"
4. Should auto-login and redirect to dashboard

## 🚀 Backend Server Issues

### Problem: Backend Import Error
The backend server has this error:
```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
1. Navigate to backend directory: `cd backend`
2. Check if `app` folder exists
3. Try running from backend directory:
   ```bash
   cd backend
   $env:PYTHONPATH = "."; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Problem: Backend Not Starting
If backend won't start:

1. **Check Python environment:**
   ```bash
   python --version
   pip list | findstr fastapi
   ```

2. **Install missing dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Check file structure:**
   ```
   backend/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py
   │   └── ...
   └── requirements.txt
   ```

## 📱 Alternative Testing Methods

### Method 1: Debug Panel
- URL: http://localhost:5173/debug-auth
- Features: Real-time status, test buttons, debug info

### Method 2: Auth Test Page
- URL: http://localhost:5173/auth-test
- Features: Automated tests, result tracking

### Method 3: Console Testing
Open browser console and run:
```javascript
// Check if auth tests are loaded
if (window.authTests) {
  authTests.runAllTests();
} else {
  console.log('Auth tests not loaded');
}
```

## 🔄 Switching Between Modes

### Enable Mockup Mode (No Backend Required)
1. Edit: `frontend/src/contexts/AuthContext.jsx`
2. Set: `const MOCKUP_MODE = true;`
3. Restart frontend server

### Enable Real API Mode (Backend Required)
1. Edit: `frontend/src/contexts/AuthContext.jsx`
2. Set: `const MOCKUP_MODE = false;`
3. Ensure backend server is running on port 8000
4. Restart frontend server

## 📋 Checklist

- [ ] Frontend server running on port 5173
- [ ] Mockup mode enabled in AuthContext
- [ ] No console errors in browser
- [ ] Debug panel shows correct status
- [ ] Login/signup forms working
- [ ] Navigation working after auth
- [ ] User data displayed in navbar

## 🆘 Still Having Issues?

If the problem persists:

1. **Check the debug panel**: http://localhost:5173/debug-auth
2. **Review console logs** for specific error messages
3. **Clear browser cache** and try again
4. **Restart frontend server** completely
5. **Check if any antivirus/firewall** is blocking localhost connections

## 📞 Support Information

**Current Configuration:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000 (not required in mockup mode)
- Mockup Mode: Enabled
- Authentication: Working with mock data

**Test URLs:**
- Main App: http://localhost:5173
- Login: http://localhost:5173/login
- Signup: http://localhost:5173/signup
- Debug Panel: http://localhost:5173/debug-auth
- Auth Tests: http://localhost:5173/auth-test 