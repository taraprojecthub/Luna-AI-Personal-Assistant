@echo off
title LUNA - Holographic Desktop Assistant
cd /d "%~dp0"

echo ========================================================
echo           STARTING LUNA DESKTOP ASSISTANT
echo ========================================================
echo.

rem Check if Ollama is running, start if needed
tasklist /fi "imagename eq ollama.exe" 2>nul | find /i "ollama.exe" >nul
if errorlevel 1 (
    where ollama >nul 2>nul
    if not errorlevel 1 (
        echo [SYS] Starting local Ollama service...
        start "" /b ollama serve
        timeout /t 2 /nobreak >nul
    )
)

cd luna_desktop
..\.venv\Scripts\python.exe main.py
if errorlevel 1 (
    echo.
    echo [SYS] LUNA exited with an error code.
    pause
)
