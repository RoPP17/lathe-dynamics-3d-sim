@echo off
title Lanzador - Simulador Dinamico del Torno (Dinamica UTA)

echo Iniciando Simulador Dinamico 3D del Torno Didactico...

if exist ".venv\Scripts\python.exe" (
    echo Usando entorno virtual local (.venv)...
    start "" ".venv\Scripts\pythonw.exe" main.py
    if %ERRORLEVEL% NEQ 0 (
        ".venv\Scripts\python.exe" main.py
    )
) else (
    echo Entorno .venv no encontrado. Ejecutando con Python del sistema...
    python main.py
)
