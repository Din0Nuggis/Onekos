@echo off
setlocal
cd /d "%~dp0"
echo.
echo  === Building Armadillo.exe ===
echo.
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install it from python.org first
  echo ^(tick "Add python.exe to PATH" in the installer^), then run this again.
  pause
  exit /b 1
)
python -m pip install --upgrade pyinstaller
if errorlevel 1 ( echo pip failed. & pause & exit /b 1 )
python -m PyInstaller --onefile --noconsole --name Armadillo --icon armadillo.ico armadillo.py
if errorlevel 1 ( echo Build failed. & pause & exit /b 1 )
copy /y "dist\Armadillo.exe" "Armadillo.exe" >nul
echo.
echo  Done! Armadillo.exe is right here next to this file.
echo.
pause
