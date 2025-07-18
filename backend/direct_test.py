#!/usr/bin/env python3

"""
Direct test of FastAPI testing endpoints using HTTP requests
"""

import requests
import json
import time
import subprocess
import os
import sys
from concurrent.futures import ThreadPoolExecutor

def start_server():
    """Start the FastAPI server using uvicorn command"""
    print("[INFO] Starting FastAPI server...")
    try:
        # Change to backend directory
        os.chdir(r"C:\xampp\htdocs\complainthubbot--alpha--44.0-implemented all\backend")
        
        # Start server using uvicorn command
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app", 
            "--host", "127.0.0.1", "--port", "8000", "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("[INFO] Waiting for server to start...")
        time.sleep(10)
        
        return process
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return None

def test_server_health():
    """Test if server is responding"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("[PASS] Server health check successful")
            print(f"[INFO] Response: {response.json()}")
            return True
        else:
            print(f"[FAIL] Server health check failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Server health check failed: {e}")
        return False

def test_testing_endpoints():
    """Test all the testing endpoints"""
    print("\n[TEST] Testing backend endpoints...")
    
    endpoints = [
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
            print(f"[TEST] Testing {endpoint}...")
            response = requests.get(f"http://127.0.0.1:8000{endpoint}", timeout=30)
            
            if response.status_code == 200:
                print(f"[PASS] {endpoint} - Status: {response.status_code}")
                data = response.json()
                results[endpoint] = {"status": "success", "data": data}
                
                # Print key results for debugging
                if "errors" in data and data["errors"]:
                    print(f"[WARN] Endpoint has errors: {data['errors']}")
                
            else:
                print(f"[FAIL] {endpoint} - Status: {response.status_code}")
                results[endpoint] = {"status": "failed", "code": response.status_code}
                
        except Exception as e:
            print(f"[ERROR] {endpoint} - Exception: {e}")
            results[endpoint] = {"status": "error", "error": str(e)}
    
    return results

def print_detailed_results(results):
    """Print detailed test results"""
    print("\n" + "="*60)
    print("DETAILED TEST RESULTS")
    print("="*60)
    
    for endpoint, result in results.items():
        print(f"\nEndpoint: {endpoint}")
        print(f"Status: {result['status']}")
        
        if result['status'] == 'success' and 'data' in result:
            data = result['data']
            
            # Print specific test results based on endpoint
            if endpoint.endswith('/database'):
                print("Database Tests:")
                for key, value in data.items():
                    if key != 'errors':
                        print(f"  - {key}: {value}")
                        
            elif endpoint.endswith('/crud'):
                print("CRUD Tests:")
                for operation_type, tests in data.items():
                    if isinstance(tests, dict) and operation_type != 'errors':
                        print(f"  {operation_type}:")
                        for test_name, test_result in tests.items():
                            print(f"    - {test_name}: {test_result}")
                            
            elif endpoint.endswith('/data-flow'):
                print("Data Flow Tests:")
                for key, value in data.items():
                    if key not in ['errors', 'test_data']:
                        print(f"  - {key}: {value}")
                        
            elif endpoint.endswith('/mock-data'):
                print("Mock Data Tests:")
                for key, value in data.items():
                    if key != 'errors':
                        print(f"  - {key}: {value}")
            
            # Print errors if any
            if 'errors' in data and data['errors']:
                print("Errors:")
                for error in data['errors']:
                    print(f"  - {error}")

def run_tests():
    """Main test runner"""
    print("Backend Testing Tool")
    print("="*40)
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("[FAIL] Could not start server")
        return
    
    try:
        # Test server health
        if not test_server_health():
            print("[FAIL] Server is not responding")
            return
        
        # Test all endpoints
        results = test_testing_endpoints()
        
        # Print results
        print_detailed_results(results)
        
        # Save results to file
        with open("backend_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n[INFO] Results saved to backend_test_results.json")
        
    except KeyboardInterrupt:
        print("\n[INFO] Tests interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
    finally:
        # Stop server
        if server_process:
            print("[INFO] Stopping server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    run_tests()