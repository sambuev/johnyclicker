@echo off
ECHO Setting up the GMB Ranker environment...

REM Check if python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO Python is not installed. Please install Python 3 and add it to your PATH.
    PAUSE
    EXIT /B 1
)

ECHO Creating Python virtual environment...
python -m venv venv
IF %ERRORLEVEL% NEQ 0 (
    ECHO Failed to create virtual environment.
    PAUSE
    EXIT /B 1
)

ECHO Installing dependencies from requirements.txt...
call venv\Scripts\activate.bat
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    ECHO Failed to install dependencies.
    PAUSE
    EXIT /B 1
)

ECHO Installing Playwright browser dependencies...
playwright install --with-deps
IF %ERRORLEVEL% NEQ 0 (
    ECHO Failed to install Playwright browsers.
    PAUSE
    EXIT /B 1
)

ECHO.
ECHO =======================================
ECHO  Installation Complete!
ECHO  To start the application, close this
ECHO  window and run the 'run.bat' file.
ECHO =======================================
ECHO.
PAUSE
