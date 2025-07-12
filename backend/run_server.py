#!/usr/bin/env python3
"""
Simple script to run the FastAPI application.
Run this from the backend directory.
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Run the FastAPI application."""
    # Set up environment variables if needed
    os.environ["PYTHONPATH"] = os.pathsep.join([
        str(Path(__file__).parent.parent),  # Project root
        str(Path(__file__).parent),         # Backend directory
        os.environ.get("PYTHONPATH", "")   # Existing PYTHONPATH
    ])
    
    # Run the FastAPI application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(Path(__file__).parent / "app")],
        reload_includes=["*.py"],
        log_level="info"
    )

if __name__ == "__main__":
    main()
