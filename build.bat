@echo off
REM ==========================================
REM Build EXE for platformer.py using Nuitka
REM ==========================================

echo Building 2D Platformer...
python -m nuitka --standalone --windows-console-mode=disable --remove-output --assume-yes-for-downloads --lto=no platformer.py

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Folder: platformer.dist/
pause
