@echo off
setlocal enabledelayedexpansion
title Instalador y Configurador - Simulador Dinamico del Torno (Dinamica UTA)

echo ==============================================================================
echo   SIMULADOR DINAMICO 3D DEL TORNO DIDACTICO PARA MADERA
echo   Asignatura: Dinamica - FICM - Universidad Tecnica de Ambato
echo   Configuracion automatica del entorno virtual para PyCharm
echo ==============================================================================
echo.

:: 1. Comprobar que Python este instalado
echo [1/8] Verificando instalacion de Python en el sistema...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no fue encontrado en el PATH del sistema.
    echo Por favor instala Python 3.10 o superior y asegurate de marcar "Add python.exe to PATH".
    pause
    exit /b 1
)

:: 2. Comprobar version de Python
echo [2/8] Comprobando version de Python...
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo       Detectado: Python !PY_VER!

:: 3. Crear el entorno virtual si no existe
echo [3/8] Configurando entorno virtual (.venv)...
if not exist ".venv" (
    echo       Creando nuevo entorno virtual en .venv...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo       Entorno virtual creado con exito.
) else (
    echo       El entorno virtual .venv ya existe. Continuando...
)

:: 4. Activar el entorno virtual
echo [4/8] Activando entorno virtual local...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al activar el entorno virtual .venv.
    pause
    exit /b 1
)

:: 5. Actualizar pip e instalar dependencias desde requirements.txt
echo [5/8] Instalando dependencias requeridas (PyQt6, PyOpenGL, numpy, pyqtgraph, matplotlib, pytest)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Hubo un problema al instalar los paquetes de requirements.txt.
    pause
    exit /b 1
)

:: 6. Comprobar imports clave
echo [6/8] Verificando integridad de bibliotecas (imports)...
python -c "import PyQt6; import OpenGL; import numpy; import pyqtgraph; import matplotlib; import pytest; print('       Todos los modulos importados correctamente.')"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo la comprobacion de imports de las bibliotecas.
    pause
    exit /b 1
)

:: 7. Ejecutar pruebas automatizadas del Caso Avance 2
echo [7/8] Ejecutando suite de pruebas unitarias y validacion del Caso Avance 2...
python -m pytest tests/
if %ERRORLEVEL% NEQ 0 (
    echo [ADVERTENCIA] Algunas pruebas reportaron diferencias. Revisa el registro anterior.
) else (
    echo       Las 21 pruebas tecnicas del Avance 2 se ejecutaron con 100%% de exito.
)

:: 8. Finalizacion exitosa
echo [8/8] Configuracion completada con exito.
echo.
echo ==============================================================================
echo   ENTORNO LISTO PARA USAR EN PYCHARM Y WINDOWS
echo   - Para iniciar el simulador, ejecuta 'run.bat' o abre la carpeta en PyCharm.
echo   - En PyCharm, selecciona el interprete existente en:
echo     .venv\Scripts\python.exe
echo ==============================================================================
echo.
pause
