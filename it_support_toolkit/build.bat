@echo off
title IT Support Toolkit - Build Script
echo ========================================
echo   IT Support Toolkit - Build Script
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo [OK] Python found

:: Install dependencies
echo.
echo [1/3] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

:: Build EXE
echo.
echo [2/3] Building standalone EXE with PyInstaller...
pyinstaller build.spec --clean
if %errorlevel% neq 0 (
    echo [ERROR] Build failed. See output above for details.
    pause
    exit /b 1
)
echo [OK] Build completed

:: Embed manifest for admin rights
echo.
echo [3/4] Embedding manifest for admin rights...
if exist "embed_manifest.bat" (
    call embed_manifest.bat
)
echo [OK] Manifest processing done

:: Success
echo.
echo [4/4] Build complete!
echo.
echo Output: dist\ITSupportToolkit.exe
echo.
echo NOTE: The EXE requires Administrator privileges.
echo       Right-click and select "Run as administrator".
echo.
pause
