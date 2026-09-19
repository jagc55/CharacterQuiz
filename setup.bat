@echo off
chcp 65001 >nul
title Instalador - CharacterQuiz (Adivina el Personaje)

echo ==========================================================
echo   🎮 INSTALADOR AUTOMÁTICO - CHARACTER QUIZ 🎮
echo ==========================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

echo.
echo Presione cualquier tecla para salir...
pause >nul
