@echo off
chcp 65001 > nul
echo ========================================
echo   Bridge Master - Simple Version
echo   No font issues, English only
echo ========================================
echo.

REM Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check pip
where pip >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: pip not found!
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Show Python version
echo Python version:
python --version

REM Install dependencies
echo.
echo Step 1: Installing dependencies...
echo pygame, pymunk, pyinstaller
pip install pygame pymunk pyinstaller

if %errorlevel% neq 0 (
    echo WARNING: Installation may have failed
    echo Try running as Administrator or use:
    echo   pip install --user pygame pymunk pyinstaller
    echo.
    pause
)

REM Check if bridge_game_simple.py exists
if not exist "bridge_game_simple.py" (
    echo ERROR: bridge_game_simple.py not found!
    echo Current directory:
    dir *.py
    pause
    exit /b 1
)

echo.
echo Step 2: Building simple version...
echo This version has NO font issues!
echo Command: pyinstaller --onefile --console --name "BridgeMaster_Simple" bridge_game_simple.py

pyinstaller --onefile --console --name "BridgeMaster_Simple" bridge_game_simple.py

if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    echo Check error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS: Simple version built!
echo EXE location: %cd%\dist\BridgeMaster_Simple.exe
echo.
echo Features:
echo 1. NO font issues - uses symbols instead of text
echo 2. English only interface
echo 3. Keyboard shortcuts: W=Wood, S=Steel, T=Test, ESC=Exit
echo.
echo To run:
echo 1. Double click: dist\BridgeMaster_Simple.exe
echo 2. Or command line: dist\BridgeMaster_Simple.exe
echo.
echo If EXE doesn't run:
echo 1. Install Visual C++ Redistributable
echo 2. Run as Administrator
echo ========================================
echo.
pause