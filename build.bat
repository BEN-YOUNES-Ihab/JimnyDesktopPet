@echo off
:: ─────────────────────────────────────────────────────
:: build.bat  –  Build JimnyDesktopPet as a standalone .exe
:: Requires: Python 3.10+  (tkinter is included by default)
:: ─────────────────────────────────────────────────────

echo [1/4] Installing build dependencies...
pip install pyinstaller pillow --quiet

echo [2/4] Generating sprite frames...
python gen_frames.py

echo [3/4] Bundling into single .exe...
pyinstaller ^
  --onefile ^
  --windowed ^
  --name JimnyDesktopPet ^
  --add-data "frames;frames" ^
  jimny_pet.py

echo [4/4] Done!
echo.
echo  Your standalone exe is at:  dist\JimnyDesktopPet.exe
echo  Copy it anywhere — no Python, no install needed.
pause
