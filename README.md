# Desktop Cat Pet v1.0 (Accurate Accessories & Double-Click Jump Edition)

A lightweight, animated cartoon desktop pet cat for Windows. Features compact full-body pixel art styling with precise accessories and interactive controls.

---

## What's New in v1.0

1. **Accurate Accessory Placement**:
   - **Pink Bow**: Sticks directly on the cat's head/ear in all positions.
   - **Red Collar**: Wraps around the cat's neck with a golden bell.
2. **Double Left Click Big Jump**:
   - Double left-clicking the cat triggers a **bigger, happy leap** with hearts and *"Hop! 🐾"*.
3. **Clean Meow Hover Greeting**:
   - Hovering over the cat displays a cute greeting bubble with your name and meow:
     `Hello Simon! Meow~` (or `Hello! Meow~`).
4. **Cursor Stillness Sit-Down**:
   - When the cursor stops moving, the cat sits down comfortably.
5. **Continuous Scrolling React**:
   - Paper unroll animation continues as long as you scroll the mouse wheel.
6. **Lively Idle Variety**:
   - Random playful actions (playing with yarn, grooming, rolls, hops, thought bubbles).
7. **Standalone Version 10 Executable**: Outputs to [`dist/DesktopCat_v1.exe`](file:///d:/Study/Cattu/dist/DesktopCat_v10.exe).

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Application
```bash
python main.py
```

---

## Building Standalone Executable (`DesktopCat_v1.exe`)

Run the build script:
```cmd
build.bat
```

Or execute PyInstaller directly:
```bash
pyinstaller --clean --onefile --noconsole --name DesktopCat_v10 --icon=assets/cat.ico --add-data "assets;assets" --add-data "skins;skins" --add-data "accessories;accessories" main.py
```
