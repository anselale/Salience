@echo off

REM Activate virtual environment
call venv\Scripts\activate

REM Upgrade library
pip install --upgrade mylibrary

REM Run tests
python -m unittest discover tests

REM Deactivate virtual environment 
call venv\Scripts\deactivate.bat
