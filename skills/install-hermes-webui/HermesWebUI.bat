@echo off
setlocal enabledelayedexpansion

title Hermes WebUI - Universal One-Click Installer
cls

echo ========================================================================
echo       Hermes WebUI - Automatic Standalone Installer & Launcher
echo ========================================================================
echo.

set "INSTALL_DIR=%USERPROFILE%\hermes-webui"
set "HERMES_DIR=%USERPROFILE%\.hermes\hermes-agent"

:: 1. Check Python
echo [1/5] Checking Python Runtime (Python 3.11+ required)...
set "PYTHON_CMD="

for %%P in (python3.13 python3.12 python3.11 python py) do (
    if not defined PYTHON_CMD (
        %%P -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
        if !ERRORLEVEL! equ 0 (
            set "PYTHON_CMD=%%P"
        )
    )
)

if not defined PYTHON_CMD (
    echo [*] Compatible Python 3.11+ not found. Installing Python 3.12 via winget...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
    python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set "PYTHON_CMD=python"
    ) else (
        echo [!] Could not verify Python 3.11+. Please install Python 3.11, 3.12, or 3.13 manually.
        pause
        exit /b 1
    )
)
echo [OK] Python runtime verified: !PYTHON_CMD!

:: 2. Check Git
echo.
echo [2/5] Checking Git...
where git >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [*] Git not found. Installing Git via winget...
    winget install -e --id Git.Git --silent --accept-package-agreements --accept-source-agreements
    set "PATH=%ProgramFiles%\Git\cmd;%PATH%"
)
echo [OK] Git ready.

:: 3. Clone or Update Hermes WebUI
echo.
echo [3/5] Setting up Hermes WebUI repository...
if not exist "%INSTALL_DIR%" (
    echo [*] Cloning Hermes WebUI to %INSTALL_DIR%...
    git clone https://github.com/nesquena/hermes-webui.git "%INSTALL_DIR%"
) else (
    echo [*] Updating Hermes WebUI...
    cd /d "%INSTALL_DIR%"
    git pull --quiet 2>nul
)

:: 4. Connect Hermes Agent Core
echo.
echo [4/5] Connecting Hermes Agent Core...
if not exist "%HERMES_DIR%" (
    echo [*] Downloading Hermes Agent core to %HERMES_DIR%...
    if not exist "%USERPROFILE%\.hermes" mkdir "%USERPROFILE%\.hermes"
    git clone --depth 1 https://github.com/NousResearch/hermes-agent.git "%HERMES_DIR%"
)
echo [OK] Hermes Agent linked.

:: 5. Setup venv & dependencies
echo.
echo [5/5] Building environment ^& starting server...
cd /d "%INSTALL_DIR%"
if not exist ".venv" (
    "%PYTHON_CMD%" -m venv .venv
)

set "VENV_PYTHON=%INSTALL_DIR%\.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    set "VENV_PYTHON=%PYTHON_CMD%"
)

"%VENV_PYTHON%" -m pip install --quiet --upgrade pip setuptools wheel
if exist "requirements.txt" (
    "%VENV_PYTHON%" -m pip install --quiet -r requirements.txt
)
if exist "%HERMES_DIR%\requirements.txt" (
    "%VENV_PYTHON%" -m pip install --quiet -r "%HERMES_DIR%\requirements.txt"
)
"%VENV_PYTHON%" -m pip install --quiet psutil edge-tts python-docx openpyxl python-pptx

set "HERMES_WEBUI_AGENT_DIR=%HERMES_DIR%"
set "PYTHONPATH=%HERMES_DIR%;%PYTHONPATH%"

start "" http://127.0.0.1:8787
"%VENV_PYTHON%" server.py

pause
