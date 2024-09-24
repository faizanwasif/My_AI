#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Please install Python3 and try again."
    exit
fi

# Check if venv is installed and install it if necessary
if ! python3 -m venv --help &> /dev/null
then
    echo "Installing virtual environment tools..."
    python3 -m ensurepip --upgrade
    python3 -m pip install --upgrade pip
    python3 -m pip install virtualenv
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install required packages
if [ -f "requirements.txt" ]; then
    echo "Installing required packages from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found, skipping package installation."
fi

# Run the main Python script
if [ -f "main.py" ]; then
    echo "Running the Python script..."
    python main.py
else
    echo "main.py not found, skipping script execution."
fi

# Deactivate virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Script completed successfully."
