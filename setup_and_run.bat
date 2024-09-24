@echo off

:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b
)

:: Check if venv is installed and install it if necessary
python -m venv --help >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Installing virtual environment...
    python -m ensurepip --upgrade
    python -m pip install --upgrade pip
    python -m pip install virtualenv
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

:: Install required packages
echo Installing required packages...
pip install -r requirements.txt

:: Run the main Python script
echo Running the Python script...
python main.py

:: Deactivate virtual environment
echo Deactivating virtual environment...
deactivate

echo Script completed successfully.
pause
