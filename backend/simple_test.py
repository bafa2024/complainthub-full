#!/usr/bin/env python3

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test basic imports"""
    print("[TEST] Testing imports...")
    try:
        import fastapi
        print("[PASS] FastAPI imported")
        
        from app.main import app
        print("[PASS] Main app imported")
        
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """Test app creation"""
    print("[TEST] Testing app creation...")
    try:
        from app.main import app
        print(f"[INFO] App title: {app.title}")
        print(f"[INFO] App version: {app.version}")
        print("[PASS] App created successfully")
        return True
    except Exception as e:
        print(f"[FAIL] App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Simple Backend Test")
    print("="*30)
    
    success = test_imports()
    if success:
        success = test_app_creation()
    
    if success:
        print("\n[SUCCESS] Basic tests passed!")
    else:
        print("\n[FAILED] Tests failed!")