#!/usr/bin/env python3

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    print("Testing imports...")
    
    # Test basic FastAPI import
    import fastapi
    print("✓ FastAPI imported successfully")
    
    # Test uvicorn import
    import uvicorn
    print("✓ Uvicorn imported successfully")
    
    # Test SQLAlchemy import
    import sqlalchemy
    print("✓ SQLAlchemy imported successfully")
    
    # Test app import
    from app.main import app
    print("✓ App imported successfully")
    
    print("\nAll imports successful! Server should be able to start.")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1) 