# Authentication Testing Guide

## Overview
This guide provides comprehensive testing instructions for the customer signup and login functionality in the ComplaintHub application.

## 🚀 Quick Start

### 1. Start the Frontend Server
```bash
cd frontend
npm run dev
```
The application will be available at: http://localhost:5173

### 2. Access Testing Pages
- **Authentication Test Page**: http://localhost:5173/auth-test
- **Login Page**: http://localhost:5173/login
- **Signup Page**: http://localhost:5173/signup

## 🧪 Testing Modes

### Mockup Mode (Default)
- **Status**: Enabled by default
- **Purpose**: Test UI functionality without backend
- **Features**: 
  - Instant login/signup responses
  - Mock user data
  - No API calls required

### Real API Mode
- **Status**: Disabled by default
- **Purpose**: Test with actual backend integration
- **Requirements**: Backend server running on port 8000

## 📋 Test Scenarios

### 1. Login Functionality Tests

#### Test Case 1.1: Valid Login
**Steps:**
1. Navigate to http://localhost:5173/login
2. Enter valid email: `test@example.com`
3. Enter valid password: `password123`
4. Click "Login" button
5. Verify successful navigation to dashboard

**Expected Result:**
- User is authenticated
- Redirected to dashboard
- User data displayed in navbar

#### Test Case 1.2: Invalid Login
**Steps:**
1. Navigate to login page
2. Enter invalid email: `invalid-email`
3. Enter password: `password123`
4. Click "Login" button

**Expected Result:**
- Error message displayed
- User remains on login page
- Form validation shows email error

#### Test Case 1.3: Empty Fields
**Steps:**
1. Navigate to login page
2. Leave email field empty
3. Leave password field empty
4. Click "Login" button

**Expected Result:**
- Form validation prevents submission
- Required field indicators shown
- No API call made

### 2. Signup Functionality Tests

#### Test Case 2.1: Valid Signup
**Steps:**
1. Navigate to http://localhost:5173/signup
2. Fill all required fields:
   - First Name: `John`
   - Last Name: `Doe`
   - Email: `john.doe@example.com`
   - Phone: `+1234567890`
   - Password: `password123`
   - Confirm Password: `password123`
3. Check "Terms of Service" checkbox
4. Click "Register" button

**Expected Result:**
- Account created successfully
- User automatically logged in
- Redirected to dashboard

#### Test Case 2.2: Password Mismatch
**Steps:**
1. Navigate to signup page
2. Fill all fields with valid data
3. Enter different passwords in password and confirm password fields
4. Click "Register" button

**Expected Result:**
- Error message: "Passwords do not match"
- Form not submitted
- User remains on signup page

#### Test Case 2.3: Invalid Email
**Steps:**
1. Navigate to signup page
2. Enter invalid email: `invalid-email`
3. Fill other fields with valid data
4. Click "Register" button

**Expected Result:**
- Email validation error
- Form not submitted
- Clear error message displayed

### 3. Form Validation Tests

#### Test Case 3.1: Required Fields
**Steps:**
1. Navigate to signup page
2. Leave one or more required fields empty
3. Click "Register" button

**Expected Result:**
- HTML5 validation prevents submission
- Required field indicators shown
- No API call made

#### Test Case 3.2: Password Strength
**Steps:**
1. Navigate to signup page
2. Enter password less than 6 characters
3. Fill other fields with valid data
4. Click "Register" button

**Expected Result:**
- Password validation error
- Form not submitted
- Clear error message displayed

### 4. Navigation Tests

#### Test Case 4.1: Login to Dashboard
**Steps:**
1. Complete successful login
2. Verify navigation to dashboard
3. Check navbar shows user information

**Expected Result:**
- Successful navigation to `/dashboard`
- User menu visible in navbar
- Logout option available

#### Test Case 4.2: Signup to Dashboard
**Steps:**
1. Complete successful signup
2. Verify automatic login
3. Check navigation to dashboard

**Expected Result:**
- Automatic login after signup
- Navigation to `/dashboard`
- User authenticated immediately

### 5. Logout Functionality

#### Test Case 5.1: Logout
**Steps:**
1. Login to the application
2. Click logout button in navbar
3. Verify logout behavior

**Expected Result:**
- User logged out
- Redirected to home page
- Login/signup options visible in navbar

## 🔧 Debugging

### Console Testing
Open browser console and run:
```javascript
// Run all tests
authTests.runAllTests()

// Run individual tests
authTests.testFormValidation()
authTests.testSignupValidation()
authTests.testLocalStorage()
```

### Common Issues

#### Issue 1: Form Not Submitting
**Symptoms:** Clicking submit button does nothing
**Solutions:**
- Check browser console for JavaScript errors
- Verify all required fields are filled
- Check form validation messages

#### Issue 2: Navigation Not Working
**Symptoms:** Login/signup successful but no redirect
**Solutions:**
- Check React Router configuration
- Verify navigation logic in components
- Check for authentication state issues

#### Issue 3: Mockup Mode Issues
**Symptoms:** Tests not working as expected
**Solutions:**
- Verify MOCKUP_MODE is set to true in AuthContext
- Check mock user data configuration
- Restart development server

## 📊 Test Results Tracking

### Automated Test Results
The testing page at `/auth-test` provides:
- Real-time test execution
- Success/failure status
- Timestamp tracking
- Detailed error messages

### Manual Test Checklist
- [ ] Login form validation
- [ ] Signup form validation
- [ ] Password confirmation
- [ ] Error message display
- [ ] Loading states
- [ ] Navigation after auth
- [ ] Logout functionality
- [ ] Responsive design
- [ ] Browser compatibility

## 🚨 Error Handling

### Expected Error Messages
- **Invalid Email**: "Please enter a valid email address"
- **Password Mismatch**: "Passwords do not match"
- **Required Fields**: "This field is required"
- **Network Error**: "No response from server. Please check your network connection"
- **Login Failed**: "Login failed. Please try again."
- **Signup Failed**: "Signup failed. Please try again."

### Error Logging
All errors are logged to browser console with:
- Error type and message
- Stack trace for debugging
- Timestamp of occurrence

## 🔄 Switching Between Modes

### Enable Real API Mode
1. Edit `frontend/src/contexts/AuthContext.jsx`
2. Set `MOCKUP_MODE = false`
3. Ensure backend server is running
4. Restart frontend development server

### Enable Mockup Mode
1. Edit `frontend/src/contexts/AuthContext.jsx`
2. Set `MOCKUP_MODE = true`
3. Restart frontend development server

## 📱 Responsive Testing

### Screen Sizes to Test
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

### Key Responsive Features
- Collapsible navbar
- Form layout adaptation
- Button sizing
- Text readability
- Touch-friendly interactions

## ✅ Success Criteria

### Login Success
- [ ] User can enter valid credentials
- [ ] Form validates input correctly
- [ ] User is authenticated
- [ ] Navigation to dashboard works
- [ ] User data displayed correctly
- [ ] Logout functionality works

### Signup Success
- [ ] User can fill all required fields
- [ ] Password confirmation works
- [ ] Form validation prevents invalid submissions
- [ ] Account creation successful
- [ ] Automatic login after signup
- [ ] Navigation to dashboard works

### Error Handling Success
- [ ] Invalid inputs show appropriate errors
- [ ] Network errors handled gracefully
- [ ] User-friendly error messages
- [ ] Form state preserved on errors
- [ ] Loading states work correctly

## 🎯 Performance Testing

### Load Testing
- Test with multiple concurrent users
- Verify form submission performance
- Check navigation responsiveness
- Monitor memory usage

### Browser Testing
- **Chrome**: Latest version
- **Firefox**: Latest version
- **Safari**: Latest version
- **Edge**: Latest version

## 📝 Reporting

### Test Report Template
```
Test Date: [Date]
Tester: [Name]
Environment: [Browser/OS]

Login Tests:
- [ ] Valid login: PASS/FAIL
- [ ] Invalid login: PASS/FAIL
- [ ] Empty fields: PASS/FAIL

Signup Tests:
- [ ] Valid signup: PASS/FAIL
- [ ] Password mismatch: PASS/FAIL
- [ ] Invalid email: PASS/FAIL

Navigation Tests:
- [ ] Login to dashboard: PASS/FAIL
- [ ] Signup to dashboard: PASS/FAIL
- [ ] Logout: PASS/FAIL

Issues Found:
- [List any issues encountered]

Recommendations:
- [List any improvements needed]
```

This testing guide ensures comprehensive coverage of the authentication functionality and helps identify any issues before deployment. 