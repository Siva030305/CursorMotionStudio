@echo off
setlocal enabledelayedexpansion

echo ========================================================================
echo               Cursor Motion Studio - Production Build Script
echo ========================================================================

:: Determine Python environment (prefer venv if present)
if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
    echo [*] Using local virtual environment: venv
) else (
    set "PYTHON_EXE=python"
    echo [*] Using global Python environment
)

:: Create directories
if not exist "dist\exe" mkdir "dist\exe"
if not exist "build" mkdir "build"

echo [*] Cleaning previous build artifacts...
if exist "dist\CursorMotionStudio.exe" del /f /q "dist\CursorMotionStudio.exe"
if exist "dist\exe\CursorMotionStudio.exe" del /f /q "dist\exe\CursorMotionStudio.exe"
if exist "dist\CursorMotionStudio-Portable.zip" del /f /q "dist\CursorMotionStudio-Portable.zip"

echo [*] Compiling standalone executable with PyInstaller...
!PYTHON_EXE! -m PyInstaller --noconfirm --clean --onefile --windowed --name "CursorMotionStudio" --icon "assets/icons/app_icon.ico" --add-data "assets;assets" --add-data "qt.conf;." main.py

if %errorlevel% neq 0 (
    echo [!] Build failed during PyInstaller compilation.
    exit /b %errorlevel%
)

:: Move executable to dist\exe\
echo [*] Organizing output executable...
copy /y "dist\CursorMotionStudio.exe" "dist\exe\CursorMotionStudio.exe"

:: Package into portable ZIP
echo [*] Generating portable ZIP archive...
!PYTHON_EXE! -c "import os, zipfile; zip_path = os.path.join('dist', 'CursorMotionStudio-Portable.zip'); z = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED); z.write(os.path.join('dist', 'exe', 'CursorMotionStudio.exe'), arcname='CursorMotionStudio.exe'); z.write('README.txt', arcname='README.txt'); z.write('qt.conf', arcname='qt.conf'); z.close(); print('Portable ZIP created at:', zip_path)"

echo ========================================================================
echo [SUCCESS] Build completed successfully!
echo Standalone EXE: dist\exe\CursorMotionStudio.exe
echo Portable ZIP  : dist\CursorMotionStudio-Portable.zip
echo ========================================================================
