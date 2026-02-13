@echo off
REM AI Sakhi - Diagram Generation Script using Docker
REM This script uses Docker to generate architecture diagrams (no WSL setup required)

echo ======================================================================
echo AI Sakhi Architecture Diagram Generator (Docker)
echo ======================================================================
echo.
echo This script will:
echo   1. Use Docker to create a temporary container
echo   2. Install required packages inside the container
echo   3. Generate architecture diagrams
echo   4. Save PNG files to generated-diagrams folder
echo.
echo Requirements:
echo   - Docker Desktop must be running
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Checking if Docker is running...
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Docker is not running
    echo Please start Docker Desktop and try again
    echo.
    pause
    exit /b 1
)

echo Docker is running!
echo.
echo Generating diagrams (this may take 2-3 minutes on first run)...
echo.

docker run --rm -v "%CD%":/app -w /app python:3.10-slim bash -c "apt-get update && apt-get install -y graphviz && pip install diagrams && python generate_ai_sakhi_diagram.py"

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
