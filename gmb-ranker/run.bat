@echo off
ECHO Starting GMB Ranker Application...

REM Check if the virtual environment exists.
IF NOT EXIST venv (
    ECHO Virtual environment not found.
    ECHO Please run install.bat first.
    PAUSE
    EXIT /B 1
)

ECHO Activating virtual environment...
call venv\Scripts\activate.bat

ECHO Launching application...
python app.py
