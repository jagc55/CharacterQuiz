#!/usr/bin/env bash
# Script de instalación automática para sistemas Linux / macOS / VPS

set -e

echo "=========================================================="
echo " 🎮 INSTALADOR AUTOMÁTICO - CANAL ADIVINA EL PERSONAJE 🎮"
echo "=========================================================="
echo ""

# 1. Comprobar / Instalar Python
echo "[1/4] Comprobando Python..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 no encontrado. Intentando instalar mediante apt/brew..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv ffmpeg
    elif command -v brew &> /dev/null; then
        brew install python ffmpeg
    else
        echo "Por favor, instala Python 3 y FFmpeg en tu sistema manualmente."
        exit 1
    fi
else
    echo "OK: $(python3 --version)"
fi

# 2. Comprobar FFmpeg
echo "[2/4] Comprobando FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg no encontrado. Instalando..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y ffmpeg
    elif command -v brew &> /dev/null; then
        brew install ffmpeg
    fi
else
    echo "OK: FFmpeg detectado."
fi

# 3. Crear carpetas
echo "[3/4] Comprobando carpetas del proyecto..."
mkdir -p Blurred_characters assets/characters assets/audio data src/uploaders
echo "OK: Carpetas verificadas."

# 4. Instalar librerías
echo "[4/4] Instalando dependencias de Python..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# 5. .env
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "Archivo .env creado."
fi

echo ""
echo "=========================================================="
echo " 🎉 ¡INSTALACIÓN COMPLETADA CON ÉXITO! 🎉"
echo "=========================================================="
echo "Ejecuta: python3 main.py --once"
echo ""
