@echo off
REM Quick run script - activates venv and runs simulation

if not exist "venv" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python main.py
