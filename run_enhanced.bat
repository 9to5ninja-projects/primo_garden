@echo off
REM Quick run script for enhanced mode v0.2.0

if not exist "venv" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python main_enhanced.py
