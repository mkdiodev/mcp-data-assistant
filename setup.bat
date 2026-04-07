@echo off
REM ============================================
REM MCP Data Assistant - Setup Script (uv)
REM ============================================

echo.
echo ============================================
echo MCP Data Assistant - Setup
echo ============================================
echo.

REM Check if uv is installed
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] uv not found. Installing...
    pip install uv
)

echo [+] Creating virtual environment...
uv venv

echo [+] Installing dependencies...
uv pip install -r requirements.txt

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next Steps:
echo 1. Copy backend\.env.example to backend\.env
echo 2. Edit backend\.env with your database credentials
echo 3. Start LM Studio on port 1234
echo 4. Run start-backend.bat in Terminal 1
echo 5. Run start-frontend.bat in Terminal 2
echo.
pause