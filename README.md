# Onekos - Desktop Pet Collection

A cute collection of 17 desktop pets that follow your cursor or play autonomously!

## 🐾 Features

- **17 Animals**: Armadillo, Wolf, Fox, Cat, Rabbit, Fish, Lizard, Bee, Butterfly, Spider, Frog, Dragon, Unicorn, Penguin, Owl, Ladybug, Snake
- **8 Accessories**: Top Hat, Bow, Glasses, Crown, Flower, Santa Hat, Witch Hat
- **Playtime Mode**: Autonomous wandering
- **Keyboard Shortcut**: Ctrl+Alt+H opens menu
- **Customizable Size**: Small, Medium, Large, Huge

## 🚀 Quick Start

### Run from Python
```bash
pythonw onekos.py
```

### Command Line Options
```bash
pythonw onekos.py --animal fox --scale 4 --playtime
```

### Controls
- **Left-click**: Pet your animal
- **Right-click**: Open menu
- **Ctrl+Alt+H**: Open menu

## 📦 Creating an EXE File

### Method 1: Using build_exe.bat (Windows)
1. Open Command Prompt in this folder
2. Run: `build_exe.bat`
3. Your executable will be at: `dist/Onekos.exe`

### Method 2: Manual PyInstaller
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build the executable:
   ```bash
   pyinstaller --onefile --windowed --icon=armadillo/armadillo.ico --name Onekos onekos.py
   ```
3. Find your EXE in the `dist/` folder

### Method 3: Using the spec file
```bash
pyinstaller Onekos.spec
```

## 📁 Files
- `onekos.py` - Main script
- `build_exe.bat` - Batch file to build EXE
- `Onekos.spec` - PyInstaller configuration
- `armadillo/armadillo.ico` - Icon file

## 🎯 Menu Options
- **Animal**: Switch between 17 animals
- **Accessory**: Add accessories to your pet
- **Playtime Mode**: Toggle autonomous movement
- **Size**: Change pet size
- **Take a nap**: Put pet to sleep
- **Roll over here**: Pet rolls to cursor
- **Quit**: Close the program
