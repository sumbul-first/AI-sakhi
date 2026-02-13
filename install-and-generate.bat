@echo off
REM AI Sakhi - Install Dependencies and Generate Diagrams in WSL

echo ======================================================================
echo AI Sakhi - Install Dependencies and Generate Diagrams
echo ======================================================================
echo.
echo This will:
echo   1. Install required packages in WSL (requires sudo password)
echo   2. Generate architecture diagrams
echo   3. Save PNG files to generated-diagrams folder
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo ======================================================================
echo Step 1: Installing dependencies in WSL...
echo ======================================================================
echo.
echo You will be prompted for your sudo password in the WSL window.
echo.

REM Run the installation script in WSL
wsl -d Ubuntu-22.04 bash install-wsl-dependencies.sh

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ======================================================================
    echo ERROR: Installation failed
    echo ======================================================================
    echo.
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo Step 2: Generating architecture diagrams...
echo ======================================================================
echo.

REM Generate diagrams
wsl -d Ubuntu-22.04 bash -c "python3 generate_ai_sakhi_diagram.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ======================================================================
    echo ERROR: Diagram generation failed
    echo ======================================================================
    echo.
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo ✅ SUCCESS! Diagrams generated successfully
echo ======================================================================
echo.
echo Generated files:
echo   - generated-diagrams\ai_sakhi_architecture.png
echo   - generated-diagrams\ai_sakhi_architecture_simplified.png
echo.
echo You can now view these files in File Explorer or VS Code.
echo.
pause
