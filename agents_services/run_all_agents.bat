@echo off
REM Run All Agent Services - Windows Batch Script
REM Double-click this file to start all agents

echo.
echo ========================================
echo Starting All Agent Services
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Run the Python script
python "%~dp0run_all_agents.py"

REM If the script exits, pause so user can see any errors
if errorlevel 1 (
    echo.
    echo Script exited with an error
    pause
)
