# Jimny Desktop Pet — Windows

A pixel-art Suzuki Jimny that drives across your Windows desktop — bouncing off screen edges, splashing through water crossings, and roaming wherever you want it.

> **Original concept and pixel-art assets by [steelfox999](https://github.com/steelfox999/JimnyDesktopPet).**

---

## Quick Start

### Option 1 — Build a standalone .exe (Recommended)

Double-click **`BUILD_EXE.bat`**

The script will automatically:
- Download portable Python 3.12 if needed (no admin rights, no system install)
- Install all dependencies locally
- Generate sprite frames
- Compile everything into a single `dist\JimnyDesktopPet.exe`

The resulting `.exe` is fully self-contained — no Python, no runtime, no installer needed. Copy it to any Windows PC and double-click.

### Option 2 — Run directly (Python 3.10+ required)

Double-click **`RUN_DIRECT.bat`**

---

## Controls

| Action | How |
|---|---|
| Grab & move | Click and drag the car anywhere on screen |
| Drop | Release mouse button — car stays where you put it |
| Settings | Right-click → Settings… |
| Pause / Resume | Right-click → Pause |
| Quit | Right-click → Quit Jimny |

---

## Features

- **12-frame driving animation** with smooth pixel-art scaling
- **Random water crossing events** — 21-frame splash animation triggers occasionally
- **Drag to reposition** — single-click drag, drops exactly where you leave it
- **Roam mode** — car drifts randomly in both horizontal and vertical directions, bouncing off all screen edges
- Always on top, fully transparent overlay
- Reverses direction at screen edges
- Settings panel: size (0.5×–8×), speed, roam toggle, and pause
- Zero network access, zero data saved

---

## Settings

| Setting | Description |
|---|---|
| Size | Scale the Jimny from 0.5× to 8× |
| Speed | How fast it drives (0.5–10) |
| Roam freely | Enables random vertical movement in addition to horizontal — the car bounces around the whole screen |
| Paused | Freeze the car in place |

---

## Files

| File | Purpose |
|---|---|
| `jimny_pet.py` | Main app — single file |
| `gen_frames.py` | Generates pixel-art sprite PNGs |
| `BUILD_EXE.bat` | Downloads Python if needed, builds .exe |
| `RUN_DIRECT.bat` | Runs directly if you have Python 3.10+ |
| `frames/` | Pre-generated sprite frames (ready to use) |

---

## Credits

Original concept, pixel art, and sprite assets by **[steelfox999](https://github.com/steelfox999/JimnyDesktopPet)** !

---

MIT License