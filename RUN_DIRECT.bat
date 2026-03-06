@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set PYEXE=
set PYDIR=%~dp0python-local

:: Prefer our own installed Python
if exist "%PYDIR%\python.exe" (
    "%PYDIR%\python.exe" -c "import tkinter" >nul 2>&1
    if not errorlevel 1 ( set PYEXE=%PYDIR%\python.exe & goto :run )
)

:: Try system Python
for %%P in (python.exe python3.exe) do (
    if not defined PYEXE (
        where %%P >nul 2>&1
        if not errorlevel 1 (
            %%P -c "import tkinter" >nul 2>&1
            if not errorlevel 1 set PYEXE=%%P
        )
    )
)

if not defined PYEXE (
    echo  No Python with tkinter found.
    echo  Run BUILD_EXE.bat first - it will install Python automatically.
    pause & exit /b 1
)

:run
"%PYEXE%" -m pip install pillow --quiet --disable-pip-version-check >nul 2>&1

if not exist "%~dp0frames\drive\frame_00.png" (
    "%PYEXE%" "%~dp0gen_frames.py"
)

start "" "%PYEXE%" "%~dp0jimny_pet.py"
