@echo off
REM ============================================
REM MCP Data Assistant - Frontend Startup Script
REM ============================================

echo.
echo ============================================
echo MCP Data Assistant - Frontend Startup
echo ============================================
echo.

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Start Streamlit app
echo [+] Starting Streamlit on http://localhost:8501
echo.

cd frontend
streamlit run app.py --server.headless true --server.port 8501