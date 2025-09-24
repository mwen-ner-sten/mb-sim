@echo off
REM
REM GUI Launcher for MB-Sim Modbus Simulator (Windows Batch File)
REM
REM This script provides an easy way to launch the GUI without needing to set PYTHONPATH.
REM Run this script from the project root directory.
REM

setlocal enabledelayedexpansion

REM Get the current directory (project root)
set "PROJECT_ROOT=%~dp0"
set "SRC_PATH=%PROJECT_ROOT%src"

echo 🚀 Launching MB-Sim GUI
echo 📁 Project root: %PROJECT_ROOT%
echo 📁 Source path: %SRC_PATH%
echo 🎯 Command: python -m mb_sim.gui
echo.
echo 💡 Tips:
echo    • Press Ctrl+C to exit the GUI
echo    • The GUI will show device and register management
echo    • Make sure no other Modbus server is running on port 1502
echo ====================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Python not found. Please install Python 3.11+
        pause
        exit /b 1
    ) else (
        set "PYTHON_CMD=python3"
    )
) else (
    set "PYTHON_CMD=python"
)

echo Using Python command: %PYTHON_CMD%

REM Set PYTHONPATH
set "PYTHONPATH=%SRC_PATH%"

REM Launch the GUI
%PYTHON_CMD% -m mb_sim.gui

pause