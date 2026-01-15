@echo off
echo 🚀 Starting bot configuration for Windows...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH. Please install Python from python.org
    pause
    exit /b
)

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Install dependencies
echo Installing dependencies...
call venv\Scripts\activate
pip install -r requirements_purger.txt

echo.
echo ✅ Configuration finished!
echo To run the bot, use:
echo venv\Scripts\python purger_bot.py
echo.
pause
