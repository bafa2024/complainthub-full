#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Backend test runner script
Tests the FastAPI backend functionality
"""

import sys
import os
import requests
import time
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test if we can import the necessary modules"""
    print("[TEST] Testing imports...")
    try:
        import fastapi
        print("[PASS] FastAPI imported successfully")
        
        from app.main import app
        print("[PASS] Main app imported successfully")
        
        from app.database import engine, get_db
        print("[PASS] Database modules imported successfully")
        
        from app.models import User, Brand, Ticket
        print("[PASS] Models imported successfully")
        
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n[TEST] Testing database connection...")
    try:
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("[PASS] Database connection successful")
            return True
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app initialization"""
    print("\n🧪 Testing FastAPI app initialization...")
    try:
        from app.main import app
        print("✅ FastAPI app initialized successfully")
        print(f"   Title: {app.title}")
        print(f"   Version: {app.version}")
        return True
    except Exception as e:
        print(f"❌ FastAPI app initialization failed: {e}")
        return False

def start_server():
    """Start the FastAPI server in background"""
    print("\n🧪 Starting backend server...")
    try:
        import uvicorn
        from app.main import app
        
        # Start server in a separate process
        config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
        server = uvicorn.Server(config)
        
        # Run server in background thread
        def run_server():
            import asyncio
            asyncio.run(server.serve())
        
        from threading import Thread
        server_thread = Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        return True
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def test_endpoints():
    """Test the testing endpoints"""
    print("\n🧪 Testing API endpoints...")
    
    base_url = "http://127.0.0.1:8000"
    
    endpoints = [
        "/health",
        "/test", 
        "/api/v1/testing/",
        "/api/v1/testing/health",
        "/api/v1/testing/database",
        "/api/v1/testing/crud",
        "/api/v1/testing/data-flow",
        "/api/v1/testing/mock-data"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            print(f"   Testing {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"   ✅ {endpoint} - Status: {response.status_code}")
                results[endpoint] = {"status": "success", "code": response.status_code, "data": response.json()}
            else:
                print(f"   ⚠️ {endpoint} - Status: {response.status_code}")
                results[endpoint] = {"status": "warning", "code": response.status_code}
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")
            results[endpoint] = {"status": "error", "error": str(e)}
    
    return results

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 Starting comprehensive backend tests...\n")
    
    test_results = {
        "imports": False,
        "database": False, 
        "fastapi": False,
        "server": False,
        "endpoints": {}
    }
    
    # Test imports
    test_results["imports"] = test_imports()
    
    if not test_results["imports"]:
        print("❌ Cannot proceed - import failures")
        return test_results
    
    # Test database
    test_results["database"] = test_database_connection()
    
    # Test FastAPI app
    test_results["fastapi"] = test_fastapi_app()
    
    if not test_results["fastapi"]:
        print("❌ Cannot proceed - FastAPI app initialization failed")
        return test_results
    
    # Start server and test endpoints
    if start_server():
        test_results["server"] = True
        test_results["endpoints"] = test_endpoints()
    
    return test_results

def print_summary(results):
    """Print test summary"""
    print("\n" + "="*60)
    print("🧪 BACKEND TEST SUMMARY")
    print("="*60)
    
    print(f"✅ Imports: {'PASS' if results['imports'] else 'FAIL'}")
    print(f"🗄️ Database: {'PASS' if results['database'] else 'FAIL'}")
    print(f"⚡ FastAPI: {'PASS' if results['fastapi'] else 'FAIL'}")
    print(f"🌐 Server: {'PASS' if results['server'] else 'FAIL'}")
    
    if results["endpoints"]:
        print(f"\n📡 API Endpoints:")
        for endpoint, result in results["endpoints"].items():
            status_icon = "✅" if result["status"] == "success" else "⚠️" if result["status"] == "warning" else "❌"
            print(f"   {status_icon} {endpoint}")
    
    # Overall status
    critical_pass = results["imports"] and results["fastapi"]
    if critical_pass and results["server"] and any(r["status"] == "success" for r in results["endpoints"].values()):
        print(f"\n🎉 OVERALL STATUS: PASS - Backend is functional!")
    elif critical_pass:
        print(f"\n⚠️ OVERALL STATUS: PARTIAL - Backend loads but some endpoints may have issues")
    else:
        print(f"\n❌ OVERALL STATUS: FAIL - Critical issues found")

if __name__ == "__main__":
    print("Backend Test Runner")
    print("=" * 40)
    
    try:
        results = run_comprehensive_tests()
        print_summary(results)
        
        # Save detailed results
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Detailed results saved to: test_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()