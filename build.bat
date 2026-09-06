@echo off
echo ===================================================
echo   Building Desktop Cat Pet v10.0 Standalone Exe...
echo ===================================================

REM Ensure assets and skins exist before building
python -c "from sprite_manager import SpriteManager; SpriteManager()"

REM Build standalone binary named DesktopCat_v10.exe
pyinstaller --clean --onefile --noconsole --name DesktopCat_v10 --icon=assets/cat.ico --add-data "assets;assets" --add-data "skins;skins" --add-data "accessories;accessories" main.py

echo.
echo ===================================================
echo   Build finished!
echo   Executable output: dist\DesktopCat_v10.exe
echo ===================================================
pause
