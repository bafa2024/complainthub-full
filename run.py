#!/usr/bin/env python3
"""
Run script for the ComplaintHub application.
This script provides an easy way to run the application with different environments.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKEND_DIR = PROJECT_ROOT / "backend"

# Add to Python path
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BACKEND_DIR))

# Ensure the backend directory exists
if not BACKEND_DIR.exists():
    print(f"Error: Backend directory not found at {BACKEND_DIR}")
    sys.exit(1)

def run_server(host="0.0.0.0", port=8000, reload=True):
    """Run the FastAPI application using uvicorn."""
    # Change working directory to backend
    os.chdir(str(BACKEND_DIR))
    
    # Ensure the app directory exists
    app_dir = BACKEND_DIR / "app"
    if not app_dir.exists():
        print(f"Error: 'app' directory not found in {BACKEND_DIR}")
        sys.exit(1)
    
    cmd = [
        sys.executable,  # Use the same Python interpreter
        "-m", "uvicorn",
        "app.main:app",
        f"--host={host}",
        f"--port={port}",
    ]
    
    if reload:
        cmd.append("--reload")
    
    env = os.environ.copy()
    # Add the current directory to PYTHONPATH
    env['PYTHONPATH'] = str(BACKEND_DIR) + os.pathsep + env.get('PYTHONPATH', '')
    env["PYTHONPATH"] = os.pathsep.join([
        str(PROJECT_ROOT),
        str(PROJECT_ROOT / "backend"),
        env.get("PYTHONPATH", "")
    ])
    
    try:
        print(f"🚀 Starting server at http://{host}:{port}")
        print("📝 API documentation available at /docs")
        print("📂 Project root:", PROJECT_ROOT)
        print("🐍 Python path:", sys.path)
        
        # Run the command in the backend directory
        subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT / "backend"),
            env=env,
            check=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Run ComplaintHub application')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    parser.add_argument('--no-reload', action='store_false', dest='reload', 
                      help='Disable auto-reload')
    
    args = parser.parse_args()
    run_server(host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()
