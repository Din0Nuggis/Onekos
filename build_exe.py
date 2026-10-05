#!/usr/bin/env python3
"""
Build script for Onekos executable
Creates a standalone .exe file using PyInstaller

Usage:
    python build_exe.py
    
This will create a dist/ directory with the executable.
"""
import os
import sys
import subprocess
import shutil

def build_exe():
    print("Building Onekos executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("PyInstaller is installed")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build with PyInstaller
    print("Running PyInstaller...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "Onekos",
        "--clean",
        "onekos.py"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("\nBuild successful!")
        print("Executable created in: dist/Onekos")
        print("\nTo run:")
        print("  On Windows: double-click dist\Onekos.exe")
        print("  On Linux/Mac: ./dist/Onekos")
    else:
        print("\nBuild failed with code:", result.returncode)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(build_exe())
