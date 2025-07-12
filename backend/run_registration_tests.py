#!/usr/bin/env python3
"""
Simple test runner for user registration tests
Run this script to test the user registration functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_user_registration import run_registration_tests

if __name__ == "__main__":
    print("🧪 User Registration Test Runner")
    print("=" * 40)
    
    # Check if required packages are installed
    try:
        import requests
        import pytest
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install required packages:")
        print("pip install requests pytest")
        sys.exit(1)
    
    # Run the tests
    success = run_registration_tests()
    
    if success:
        print("\n🎉 All registration tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        sys.exit(1) 