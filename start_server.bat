@echo off
cd backend
call ..\.venv\Scripts\activate.bat
set PYTHONPATH=.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
