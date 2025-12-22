@echo off
REM Investment Backtester - Web Application Launcher

echo ================================================================================
echo.
echo     INVESTMENT BACKTESTER - WEB INTERFACE
echo.
echo ================================================================================
echo.

REM Check if yfinance is installed
python -m pip show yfinance >nul 2>&1

if %errorlevel% neq 0 (
    echo WARNING: yfinance not installed!
    echo.
    echo Installing required packages...
    echo.
    
    REM Use Anaconda Python if available
    if exist "C:\Users\Lewis\anaconda3\python.exe" (
        echo Found Anaconda Python. Installing...
        "C:\Users\Lewis\anaconda3\python.exe" -m pip install -q yfinance flask flask-cors
    ) else (
        echo Attempting to install with system Python...
        python -m pip install yfinance flask flask-cors
    )
    
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo Please install manually with: pip install -r requirements.txt
        pause
        exit /b 1
    )
    
    echo ✓ Installation complete!
    echo.
)

echo Starting web application on http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ================================================================================
echo.

REM Use Anaconda Python if available, otherwise use system Python
if exist "C:\Users\Lewis\anaconda3\python.exe" (
    "C:\Users\Lewis\anaconda3\python.exe" app.py
) else (
    python app.py
)

pause
