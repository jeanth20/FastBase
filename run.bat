@echo off
echo Running FastBase...

REM Check if virtual environment exists
if not exist venv\Scripts\python.exe (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment and run the application
call venv\Scripts\activate
python run.py
pause
