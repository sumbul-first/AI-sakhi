@echo off
REM AI Sakhi - Diagram Generation Script for WSL
REM This script installs dependencies and generates architecture diagrams

echo ======================================================================
echo AI Sakhi Architecture Diagram Generator (WSL)
echo ======================================================================
echo.
echo This script will:
echo   1. Install required packages in WSL (requires sudo password)
echo   2. Generate architecture diagrams
echo   3. Save PNG files to generated-diagrams folder
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Step 1: Installing dependencies in WSL...
echo (You will be prompted for your sudo password)
echo.

wsl -d Ubuntu-22.04 bash -c "sudo apt-get update && sudo apt-get install -y python3-pip graphviz && pip3 install diagrams"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please check the error messages above
    echo.
    pause
    exit /b 1
)

echo.
echo Step 2: Generating architecture diagrams...
echo.

wsl -d Ubuntu-22.04 bash -c "cd /mnt/c/%CD:~3% && python3 generate_ai_sakhi_diagram.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to generate diagrams
    echo Please check the error messages above
    echo.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo SUCCESS! Diagrams generated successfully
echo ======================================================================
echo.
echo Generated files:
echo   - generated-diagrams\ai_sakhi_architecture.png
echo   - generated-diagrams\ai_sakhi_architecture_simplified.png
echo.
echo You can now view these files in File Explorer or VS Code
echo.
pause
