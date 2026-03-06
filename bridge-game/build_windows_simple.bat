@echo off
chcp 65001 > nul
title Bridge Game Packager

echo ===============================
echo  Bridge Game - Build Script
echo ===============================
echo.

REM Check Python
python --version >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.7+ from python.org
    echo And check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check pip
pip --version >nul 2>nul
if errorlevel 1 (
    echo ERROR: pip not found!
    echo Try: python -m ensurepip --upgrade
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Install dependencies
echo Step 1: Installing dependencies...
echo pygame, pymunk, pyinstaller
pip install pygame pymunk pyinstaller

if errorlevel 1 (
    echo WARNING: Installation may have failed
    echo Try running as Administrator
    echo Or use: pip install --user pygame pymunk pyinstaller
    echo.
)

REM Check if bridge_game.py exists
if not exist "bridge_game.py" (
    echo ERROR: bridge_game.py not found!
    echo Make sure you run this script in game directory
    echo Current files:
    dir *.py
    pause
    exit /b 1
)

echo.
echo Step 2: Building EXE...
echo Command: pyinstaller --onefile --console bridge_game.py
echo.

REM Build with console for debugging
pyinstaller --onefile --console bridge_game.py

if errorlevel 1 (
    echo ERROR: Build failed!
    echo Check error messages above
    pause
    exit /b 1
)

echo.
echo ===============================
echo SUCCESS: Build completed!
echo EXE location: %cd%\dist\bridge_game.exe
echo.
echo To run:
echo 1. Double click: dist\bridge_game.exe
echo 2. Or cmd: dist\bridge_game.exe
echo.
echo Troubleshooting:
echo - Install Visual C++ Redistributable
echo - Update graphics drivers
echo - Run as Administrator
echo ===============================
echo.
pause