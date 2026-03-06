@echo off
setlocal enabledelayedexpansion
title Jimny Desktop Pet - Setup
cd /d "%~dp0"

echo.
echo  ==============================================
echo   Jimny Desktop Pet - Windows Setup
echo  ==============================================
echo.

:: ── 1. Find a working Python 3.10+ WITH tkinter ───────────────────────────
set "PYEXE="
set "PYDIR=%~dp0python-local"

:: Check our own previously installed Python first
if exist "%PYDIR%\python.exe" (
    "%PYDIR%\python.exe" -c "import tkinter" >nul 2>&1
    if not errorlevel 1 (
        set "PYEXE=%PYDIR%\python.exe"
        echo  [OK] Using local Python
        goto :have_python
    )
)

:: Check system Python
for %%P in (python.exe python3.exe) do (
    if not defined PYEXE (
        where %%P >nul 2>&1
        if not errorlevel 1 (
            %%P -c "import tkinter" >nul 2>&1
            if not errorlevel 1 (
                set "PYEXE=%%P"
            )
        )
    )
)

if defined PYEXE (
    echo  [OK] Found system Python with tkinter: %PYEXE%
    goto :have_python
)

:: ── 2. Download full Python 3.12 installer, install silently locally ───────
echo  [INFO] No usable Python found. Downloading Python 3.12 (~25 MB)...
echo  [INFO] No admin rights required - installs locally only.
echo.

set "PYINST=%TEMP%\python312_installer.exe"
set "PYURL=https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"

echo  [1/4] Downloading Python 3.12...
powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol='Tls12'; (New-Object Net.WebClient).DownloadFile('%PYURL%', '%PYINST%')"
if not exist "%PYINST%" (
    echo  [ERROR] Download failed. Check your internet connection.
    pause & exit /b 1
)

echo  [2/4] Installing Python locally...
"%PYINST%" /quiet InstallAllUsers=0 TargetDir="%PYDIR%" PrependPath=0 Include_launcher=0 Include_test=0 Include_doc=0 Include_dev=0
del "%PYINST%" >nul 2>&1

if not exist "%PYDIR%\python.exe" (
    echo  [ERROR] Installation failed. Try right-clicking and "Run as administrator".
    pause & exit /b 1
)

"%PYDIR%\python.exe" -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] tkinter missing after install. Install Python manually from python.org.
    pause & exit /b 1
)

set "PYEXE=%PYDIR%\python.exe"
echo  [2/4] Python 3.12 ready.

:have_python
echo.

:: ── 3. Install Pillow + PyInstaller ───────────────────────────────────────
echo  [3/4] Installing Pillow + PyInstaller...
"%PYEXE%" -m pip install pillow pyinstaller --quiet --disable-pip-version-check
if errorlevel 1 (
    echo  [ERROR] pip install failed.
    pause & exit /b 1
)
echo  [3/4] Done.
echo.

:: ── 4. Generate frames if missing ─────────────────────────────────────────
if not exist "%~dp0frames\drive\frame_00.png" (
    echo  [GEN] Generating sprite frames...
    "%PYEXE%" "%~dp0gen_frames.py"
    if errorlevel 1 ( echo  [ERROR] Frame generation failed. & pause & exit /b 1 )
) else (
    echo  [GEN] Frames already present.
)
echo.

:: ── 5. Compile .exe ───────────────────────────────────────────────────────
echo  [4/4] Compiling JimnyDesktopPet.exe (30-90 seconds)...
echo.

set "FRAMES_SRC=%~dp0frames"
set "SCRIPT=%~dp0jimny_pet.py"
set "OUTDIR=%~dp0dist"

"%PYEXE%" -m PyInstaller --onefile --windowed --name JimnyDesktopPet --add-data "%FRAMES_SRC%;frames" --distpath "%OUTDIR%" --noconfirm --clean "%SCRIPT%"

if errorlevel 1 (
    echo.
    echo  [ERROR] Build failed. See above for details.
    pause & exit /b 1
)

if not exist "%OUTDIR%\JimnyDesktopPet.exe" (
    echo  [ERROR] Build seemed to succeed but exe not found at:
    echo          %OUTDIR%\JimnyDesktopPet.exe
    pause & exit /b 1
)

echo.
echo  ==============================================
echo   BUILD COMPLETE!
echo  ==============================================
echo.
echo   Standalone exe: %OUTDIR%\JimnyDesktopPet.exe
echo   Copy it anywhere - zero install needed.
echo.
pause