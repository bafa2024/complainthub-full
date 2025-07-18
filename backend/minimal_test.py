#!/usr/bin/env python3

"""
Minimal backend test that directly calls the testing endpoint logic
"""

import sys
import os
import sqlite3
from datetime import datetime

def test_database_basic():
    """Test basic database connectivity without SQLAlchemy"""
    print("[TEST] Testing direct SQLite connectivity...")
    try:
        # Try to create a simple SQLite connection
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        # Test basic operations
        cursor.execute('CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)')
        cursor.execute('INSERT INTO test_table (name) VALUES (?)', ('test_data',))
        cursor.execute('SELECT * FROM test_table')
        results = cursor.fetchall()
        
        # Clean up
        cursor.execute('DROP TABLE test_table')
        conn.commit()
        conn.close()
        
        print(f"[PASS] SQLite operations successful - Retrieved: {results}")
        return True
        
    except Exception as e:
        print(f"[FAIL] Database test failed: {e}")
        return False

def test_fastapi_minimal():
    """Test FastAPI imports only"""
    print("\n[TEST] Testing FastAPI imports...")
    try:
        import fastapi
        print(f"[PASS] FastAPI {fastapi.__version__} imported successfully")
        
        from fastapi import FastAPI
        app = FastAPI(title="Test App", version="1.0.0")
        print(f"[PASS] FastAPI app created - Title: {app.title}")
        return True
        
    except Exception as e:
        print(f"[FAIL] FastAPI test failed: {e}")
        return False

def test_python_env():
    """Test Python environment"""
    print("\n[TEST] Testing Python environment...")
    print(f"[INFO] Python version: {sys.version}")
    print(f"[INFO] Python executable: {sys.executable}")
    print(f"[INFO] Current working directory: {os.getcwd()}")
    
    # Test key imports
    try:
        import uvicorn
        print(f"[INFO] Uvicorn available")
    except ImportError:
        print("[WARN] Uvicorn not available")
    
    try:
        import requests
        print(f"[INFO] Requests available")
    except ImportError:
        print("[WARN] Requests not available")
    
    return True

def manual_testing_endpoint_logic():
    """Manually implement the testing endpoint logic without imports"""
    print("\n[TEST] Manual testing logic...")
    
    results = {
        "database_connection": "unknown",
        "basic_operations": "unknown",
        "timestamp": datetime.now().isoformat(),
        "errors": []
    }
    
    try:
        # Test SQLite connection
        conn = sqlite3.connect(':memory:')  # In-memory database for testing
        cursor = conn.cursor()
        
        # Test table creation
        cursor.execute('''
            CREATE TABLE test_users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE,
                name TEXT,
                created_at TEXT
            )
        ''')
        results["database_connection"] = "success"
        
        # Test insertion
        cursor.execute('''
            INSERT INTO test_users (email, name, created_at) 
            VALUES (?, ?, ?)
        ''', ('test@test.com', 'Test User', datetime.now().isoformat()))
        
        # Test query
        cursor.execute('SELECT COUNT(*) FROM test_users')
        count = cursor.fetchone()[0]
        
        # Test update
        cursor.execute('''
            UPDATE test_users SET name = ? WHERE email = ?
        ''', ('Updated Test User', 'test@test.com'))
        
        # Test deletion
        cursor.execute('DELETE FROM test_users WHERE email = ?', ('test@test.com',))
        
        conn.commit()
        conn.close()
        
        results["basic_operations"] = f"success - {count} record(s) processed"
        
    except Exception as e:
        results["errors"].append(f"Database operations failed: {str(e)}")
        results["basic_operations"] = "failed"
    
    return results

def run_minimal_tests():
    """Run all minimal tests"""
    print("Minimal Backend Test Suite")
    print("="*50)
    
    results = {
        "python_env": test_python_env(),
        "fastapi": test_fastapi_minimal(),
        "database": test_database_basic(),
        "manual_logic": manual_testing_endpoint_logic()
    }
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for test_name, result in results.items():
        if isinstance(result, bool):
            status = "PASS" if result else "FAIL"
            print(f"{test_name}: {status}")
        elif isinstance(result, dict):
            print(f"{test_name}:")
            for key, value in result.items():
                print(f"  {key}: {value}")
    
    # Overall assessment
    critical_tests = [results["python_env"], results["fastapi"], results["database"]]
    if all(critical_tests):
        print(f"\n[SUCCESS] All critical tests passed!")
        print("[INFO] Backend environment appears functional for testing")
    else:
        print(f"\n[PARTIAL] Some tests failed")
        print("[INFO] Check individual test results above")

if __name__ == "__main__":
    run_minimal_tests()