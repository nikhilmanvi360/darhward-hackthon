@echo off
REM Quick Setup Script for Conda Environment
REM Run this after conda environment is created

echo ========================================
echo AI Attendance System - Conda Setup
echo ========================================
echo.

echo Step 1: Activating conda environment...
call conda activate attendance
if errorlevel 1 (
    echo ERROR: Failed to activate environment
    echo Please ensure conda environment 'attendance' is created
    pause
    exit /b 1
)

echo.
echo Step 2: Installing dlib from conda-forge...
call conda install -c conda-forge dlib -y
if errorlevel 1 (
    echo ERROR: Failed to install dlib
    pause
    exit /b 1
)

echo.
echo Step 3: Installing face-recognition and other dependencies...
call pip install face-recognition
if errorlevel 1 (
    echo ERROR: Failed to install face-recognition
    pause
    exit /b 1
)

echo.
echo Step 4: Installing Flask and OpenCV...
call pip install Flask opencv-python numpy Pillow
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo Step 5: Initializing database...
python database.py
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To run the application:
echo   1. conda activate attendance
echo   2. python app.py
echo   3. Open browser: http://127.0.0.1:5000
echo.
echo Press any key to start the application now...
pause

python app.py
