@echo off
:: Build Onekos as a standalone executable
:: Requires PyInstaller: pip install pyinstaller

set SCRIPT=onekos.py
set OUTPUT=dist/Onekos.exe
set ICON=armadillo/armadillo.ico

echo Building Onekos.exe...
echo.

:: Check if PyInstaller is installed
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo Creating executable (this may take a minute)...
python -m PyInstaller --onefile --windowed --icon=%ICON% --name Onekos %SCRIPT%

echo.
echo ============================================
echo Build complete!
echo Your executable is at: %OUTPUT%
echo.
echo You can now run Onekos.exe directly by double-clicking it.
echo ============================================
pause
