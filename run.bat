@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title CharacterQuiz - Generador de Videos TikTok y YouTube Shorts

:menu
cls
echo =============================================================
echo   🎮 GENERADOR DE VIDEOS "ADIVINA EL PERSONAJE" 🎮
echo =============================================================
echo.
echo  [1] Generar 1 video ahora mismo (--once)
echo  [2] Iniciar generador automatico cada 4 horas (--schedule)
echo  [3] Ver catalogo de personajes y estado (--list-characters)
echo  [4] Abrir carpeta de videos (Blurred_characters)
echo  [5] Salir
echo.
echo =============================================================
set /p opt="Selecciona una opción (1-5): "

if "%opt%"=="1" (
    cls
    echo Generando video de prueba...
    python main.py --once
    echo.
    echo Proceso finalizado.
    pause
    goto menu
)

if "%opt%"=="2" (
    cls
    echo Iniciando ciclo automatico cada 4 horas...
    echo Presiona Ctrl + C para detener.
    python main.py --schedule
    pause
    goto menu
)

if "%opt%"=="3" (
    cls
    python main.py --list-characters
    echo.
    pause
    goto menu
)

if "%opt%"=="4" (
    start "" "%~dp0Blurred_characters"
    goto menu
)

if "%opt%"=="5" (
    exit
)

goto menu
