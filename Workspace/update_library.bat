@echo off
REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade the library within the virtual environment
pip install --upgrade --extra-index-url https://test.pypi.org/simple/ your-library-package

REM Run tests
python -m unittest discover -s tests

REM Deactivate the virtual environment
call venv\Scripts\deactivate.bat
