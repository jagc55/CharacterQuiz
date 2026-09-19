# ==========================================================
# Script de instalacion automatica para "CharacterQuiz" en Windows.
# Verifica e instala Python 3.12, FFmpeg y librerias necesarias.
# ==========================================================

$ErrorActionPreference = "Continue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  INSTALADOR AUTOMATICO - CANAL ADIVINA EL PERSONAJE " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Comprobar Winget
$hasWinget = Get-Command winget -ErrorAction SilentlyContinue

# 2. Comprobar / Instalar Python
Write-Host "[1/5] Comprobando instalacion de Python..." -ForegroundColor Cyan
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonCmd) {
    Write-Host "Python no encontrado en el sistema." -ForegroundColor Yellow
    if ($hasWinget) {
        Write-Host "Instalando Python 3.12 mediante winget..." -ForegroundColor Green
        winget install --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        Write-Host "ERROR: winget no disponible. Instala Python 3.12 desde https://www.python.org/downloads/" -ForegroundColor Red
        Pause
        Exit 1
    }
} else {
    $pyVersion = python --version
    Write-Host "OK: $pyVersion detectado." -ForegroundColor Green
}

# 3. Comprobar / Instalar FFmpeg
Write-Host "`n[2/5] Comprobando instalacion de FFmpeg..." -ForegroundColor Cyan
$ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue

if (-not $ffmpegCmd) {
    Write-Host "FFmpeg no encontrado en el sistema." -ForegroundColor Yellow
    if ($hasWinget) {
        Write-Host "Instalando FFmpeg mediante winget..." -ForegroundColor Green
        winget install --id Gyan.FFmpeg.Essentials --accept-source-agreements --accept-package-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        Write-Host "ADVERTENCIA: FFmpeg no esta en el PATH. Descargalo de https://ffmpeg.org/download.html" -ForegroundColor Yellow
    }
} else {
    Write-Host "OK: FFmpeg detectado correctamente." -ForegroundColor Green
}

# 4. Crear carpetas necesarias
Write-Host "`n[3/5] Verificando estructura de carpetas..." -ForegroundColor Cyan
$folders = @("Blurred_characters", "assets\characters", "assets\audio", "data", "src\uploaders")
foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "Creada carpeta: $folder" -ForegroundColor Gray
    }
}
Write-Host "OK: Carpetas verificadas (incluyendo Blurred_characters en la raiz)." -ForegroundColor Green

# 5. Instalar dependencias de Python
Write-Host "`n[4/5] Instalando dependencias de Python desde requirements.txt..." -ForegroundColor Cyan
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Hubo un problema instalando las dependencias de Python." -ForegroundColor Red
    Pause
    Exit 1
}
Write-Host "OK: Dependencias de Python instaladas con exito." -ForegroundColor Green

# 6. Preparar archivo de configuracion .env si no existe
Write-Host "`n[5/5] Comprobando archivo de configuracion .env..." -ForegroundColor Cyan
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Archivo .env creado a partir de .env.example." -ForegroundColor Green
    }
} else {
    Write-Host "OK: Archivo .env ya existe." -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  INSTALACION COMPLETADA CON EXITO! " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para generar tu primer video de prueba:" -ForegroundColor Cyan
Write-Host "   python main.py --once" -ForegroundColor White
Write-Host ""
Write-Host "Para iniciar el bot automatico cada 4 horas:" -ForegroundColor Cyan
Write-Host "   python main.py --schedule" -ForegroundColor White
Write-Host ""
Write-Host "O simplemente haz doble clic en 'run.bat'." -ForegroundColor Yellow
Write-Host ""
