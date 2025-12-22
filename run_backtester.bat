@echo off
REM Investment Backtester MVP - Run Script

echo Searching for Python installation...

REM Try python3 first
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    echo Found Python3. Running backtester...
    python3 backtester_standalone.py
    exit /b %errorlevel%
)

REM Try python
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Found Python. Running backtester...
    python backtester_standalone.py
    exit /b %errorlevel%
)

echo Python not found. Please install Python 3.8 or higher.
echo Download from: https://www.python.org/downloads/
pause
