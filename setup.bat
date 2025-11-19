@echo off
REM Primordial Garden - Quick Setup Script (Windows)

echo ==================================
echo Primordial Garden - Setup
echo ==================================
echo.

echo Checking Python version...
python --version

echo.
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ==================================
echo Setup complete!
echo ==================================
echo.
echo To run the simulation:
echo   venv\Scripts\activate
echo   python main.py
echo.
echo Or use the run.bat script:
echo   run.bat
echo.
echo Controls:
echo   SPACE: Pause/Resume
echo   1-5: Speed control
echo   S: Toggle stats
echo   R: Reset
echo   Q: Quit
echo.
pause
