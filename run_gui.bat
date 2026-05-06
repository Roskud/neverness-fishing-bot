@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title Neverness Fishing Bot

set "SCRIPT_PATH=%~f0"
set "SCRIPT_DIR=%~dp0"

net session >nul 2>&1
if errorlevel 1 (
    echo Requesting administrator rights...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath $env:SCRIPT_PATH -WorkingDirectory $env:SCRIPT_DIR -Verb RunAs"
    exit /b 0
)

set "VENV_DIR=%~dp0.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "PYTHONW_EXE=%VENV_DIR%\Scripts\pythonw.exe"
set "REQUIREMENTS=%~dp0requirements.txt"

if not exist "%REQUIREMENTS%" (
    echo requirements.txt was not found next to run_gui.bat.
    pause
    exit /b 1
)

if not exist "%PYTHON_EXE%" (
    call :find_python
    if errorlevel 1 goto no_python

    echo Creating local .venv...
    !BASE_PY! -m venv "%VENV_DIR%"
    if errorlevel 1 goto venv_failed

    echo Updating package installer...
    "%PYTHON_EXE%" -m ensurepip --upgrade >nul 2>&1
    "%PYTHON_EXE%" -m pip install --disable-pip-version-check --upgrade pip setuptools wheel
    if errorlevel 1 goto install_failed
)

echo Checking and installing dependencies...
"%PYTHON_EXE%" -m pip install --disable-pip-version-check -r "%REQUIREMENTS%"
if errorlevel 1 goto install_failed

echo Starting GUI...
if exist "%PYTHONW_EXE%" (
    start "" "%PYTHONW_EXE%" "%~dp0fishing_gui.py"
) else (
    start "" "%PYTHON_EXE%" "%~dp0fishing_gui.py"
)
exit /b 0

:find_python
set "BASE_PY="
py -3 --version >nul 2>&1
if not errorlevel 1 set "BASE_PY=py -3"
if defined BASE_PY exit /b 0

python --version >nul 2>&1
if not errorlevel 1 set "BASE_PY=python"
if defined BASE_PY exit /b 0

exit /b 1

:no_python
echo Python was not found.
echo Install Python 3.10+ with "Add python.exe to PATH", then run this file again.
start "" "https://www.python.org/downloads/windows/"
pause
exit /b 1

:venv_failed
echo Failed to create .venv.
echo Check that Python is installed correctly and this folder is writable.
pause
exit /b 1

:install_failed
echo Failed to install dependencies.
echo Check the internet connection and run run_gui.bat again.
pause
exit /b 1
