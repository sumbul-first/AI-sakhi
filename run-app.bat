@echo off
REM AI Sakhi - Quick Start Script
REM This script activates the virtual environment and starts the application

echo ================================================
echo    AI Sakhi - Starting Application
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "ai-sakhi-env\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Creating virtual environment...
    python -m venv ai-sakhi-env
    echo.
    echo Installing dependencies...
    ai-sakhi-env\Scripts\pip.exe install -r requirements.txt
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call ai-sakhi-env\Scripts\activate.bat

REM Check if app file exists
if not exist "app_integrated.py" (
    echo ERROR: app_integrated.py not found!
    echo Please make sure you're in the correct directory.
    pause
    exit /b 1
)

REM Start the application
echo.
echo Starting AI Sakhi application...
echo.
echo ================================================
echo    Application will start on port 8080
echo    Open your browser to: http://localhost:8080
echo ================================================
echo.
echo Press Ctrl+C to stop the application
echo.

python app_integrated.py

pause
