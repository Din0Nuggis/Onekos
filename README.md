# Onekos - Desktop Pet Collection

A cute desktop pet that follows your cursor with multiple animals, accessories, and fun features!

## Features

- **17 Unique Animals**: armadillo, wolf, fox, cat, rabbit, fish, lizard, bee, butterfly, spider, frog, dragon, unicorn, penguin, owl, ladybug, snake
- **8 Accessories**: tophat, bow, glasses, crown, flower, santa, witch (plus "none")
- **Playtime Mode**: Toggle autonomous wandering (pet doesn't follow cursor)
- **Keyboard Shortcut**: Ctrl+Alt+H opens the menu
- **Right-click Menu**: Change animal, accessory, size, toggle playtime mode, etc.
- **Google Docs Detection**: Types random text when you're in docs.google.com
- **Multiple Views**: Side, front, and back views with proper animations
- **Cute Designs**: Each animal has unique, cute sprite designs

## Usage

### Running from Source

```bash
# Basic usage
pythonw onekos.py

# With custom scale (size)
pythonw onekos.py --scale 4

# With specific animal
pythonw onekos.py --animal fox

# With accessory
pythonw onekos.py --accessory tophat

# With playtime mode enabled
pythonw onekos.py --playtime

# All options combined
pythonw onekos.py --scale 3 --animal cat --accessory bow --playtime
```

### Controls

- **Left Click**: Pet the animal (makes it happy)
- **Right Click**: Open context menu
- **Ctrl+Alt+H**: Open menu (keyboard shortcut)

### Menu Options

- **Animal**: Change to any of the 17 animals
- **Accessory**: Add/change accessories (8 options)
- **Playtime Mode**: Toggle autonomous wandering
- **Take a nap**: Pet curls up and sleeps
- **Dig a hole**: Pet digs into the ground
- **Roll over here**: Pet rolls to the cursor
- **Size**: Change pet size (Small, Medium, Large, Huge)
- **Quit**: Exit the application

## Building Executable

### Windows

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the build script:
   ```bash
   python build_exe.py
   ```

3. The executable will be created in `dist/Onekos.exe`

### Linux/Mac

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the build script:
   ```bash
   python build_exe.py
   ```

3. The executable will be created in `dist/Onekos`

## Requirements

- Python 3.6+
- tkinter (usually included with Python)
- PyInstaller (for building executable, optional)
- pyautogui (for Google Docs detection, optional - gracefully falls back if not installed)

## Installation

```bash
# Clone the repository
git clone https://github.com/Din0Nuggis/Onekos.git
cd Onekos

# Run directly
pythonw onekos.py

# Or build executable
python build_exe.py
```

## Troubleshooting

### Menu not working
- Make sure you're right-clicking on the pet window
- Try the Ctrl+Alt+H keyboard shortcut instead

### Animal disappears
- This was a bug in earlier versions, should be fixed now
- Try running with `--scale 3` or a different scale

### Google Docs typing not working
- Requires pyautogui: `pip install pyautogui`
- Works best on Windows
- May require accessibility permissions on Mac

### Transparency not working
- On Linux, you may need to use a compositor (like Compton)
- On Windows, transparency should work automatically

## Credits

Original armadillo code based on the classic Oneko desktop pet.
All sprite designs and additional features created for this project.

## License

MIT License - Feel free to use, modify, and distribute!
