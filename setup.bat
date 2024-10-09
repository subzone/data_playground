@echo off

REM Create a virtual environment
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install the requirements
pip install -r requirements.txt

REM Run the data grabber
python poc_implementation.py