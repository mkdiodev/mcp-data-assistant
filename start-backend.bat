@echo off
REM ============================================
REM MCP Data Assistant - Backend Startup Script
REM ============================================

echo.
echo ============================================
echo MCP Data Assistant - Backend Startup
echo ============================================
echo.

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Check if .env exists
if not exist "backend\.env" (
    echo [!] Warning: backend\.env not found!
    echo     Copy backend\.env.example to backend\.env and configure it.
    pause
    exit /b 1
)

REM Create logs directory
if not exist "logs" mkdir logs

REM Start FastAPI server
echo [+] Starting FastAPI server on http://localhost:8000
echo [+] API Docs: http://localhost:8000/docs
echo.

cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000