# CharacterQuiz: Generador Automático de Videos para TikTok & YouTube Shorts

[![Versión Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Plataforma](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/jagc55/CharacterQuiz)
[![Formato Video](https://img.shields.io/badge/video%20format-9%3A16%20%281080x1920%29-purple.svg)](https://github.com/jagc55/CharacterQuiz)
[![Caso de Estudio Portfolio](https://img.shields.io/badge/Portfolio-Caso%20de%20Estudio%20T%C3%A9cnico-success.svg?logo=markdown)](PORTFOLIO_es.md)

*Idiomas: [English](README.md) | [Español](README_es.md) • Caso de estudio para Portfolio: [Español](PORTFOLIO_es.md) | [English](PORTFOLIO.md)*

**CharacterQuiz** es un sistema completamente automatizado en **Python** para la generación, programación y publicación periódica (cada 4 horas) de videos verticales de alta retención (9:16, 1080x1920 a 30 FPS) para **TikTok** y **YouTube Shorts**.

El video presenta un formato gamificado de adivinanza de videojuegos: una **pantalla de introducción con gancho en inglés**, **transiciones cinemáticas neón gaming**, **3 personajes por video con pixelado retro progresivo** (3 PTS → 2 PTS → 1 PTO → Revelación Full HD), y una **pantalla final interactiva (Outro)** diseñada para disparar los comentarios, likes y suscripciones.

---

## Carpeta de Salida Obligatoria (`Blurred_characters/`)

Todos los videos `.mp4` generados y sus archivos `.json` de metadatos asociados se guardan automáticamente en la carpeta raíz del proyecto:
```
Blurred_characters/
├── quiz_20261021_145706_cloyster_pacman_raiden_mk.mp4
└── quiz_20261021_145706_cloyster_pacman_raiden_mk.json
```

Cada video viene acompañado de un archivo `.json` con:
- Título sugerido optimizado para viralidad y SEO
- Descripción con hashtags en tendencia (`#Shorts`, `#Gaming`, `#QuizGamer`, `#VideoGames`, etc.)
- Desglose por rondas de personajes, franquicias y plataformas
- Fondo temático utilizado y estado de subida a redes (YouTube y TikTok)

---

## Estructura del Video (Formato de 50.5 Segundos para Alta Retención)

Cada video está optimizado en 5 fases estratégicas diseñadas para maximizar la tasa de finalización algorítmica (< 60s):

```
[Pantalla Intro: 2.5s] -> [Transición: 0.5s] -> [Ronda 1: 14.5s] -> [Ronda 2: 14.5s] -> [Ronda 3: 14.5s] -> [Transición: 0.5s] -> [Outro & CTA: 3.5s]
```

### 1. Pantalla de Introducción (0.0s – 2.5s)
- **Badge superior:** `VIDEO GAME CHALLENGE`
- **Texto de gancho (100% en inglés):**
 > **CAN YOU GUESS** 
 > **THE FOLLOWING** 
 > **VIDEO GAME CHARACTERS?**
- **3 Cajas de botín misteriosas:** Vista previa visual de las Rondas 1 (Oro), 2 (Cian) y 3 (Magenta) con signos de interrogación `?` luminosos.
- **Reglas y puntuación:** *"3 CHARACTERS • 9 POINTS MAX • Guess before the pixels fully clear! The faster you guess, the more points you get!"*
- **Desafío para retención:** *"ARE YOU A TRUE GAMER? CAN YOU SCORE 9/9 POINTS?"*
- **Llamada de arranque:** *"GET READY TO PLAY!"*

### 2. Transiciones Cinemáticas Neón (2x 0.5s)
- **Push Slide Cúbico Hermite:** Desplazamiento fluido donde la pantalla saliente se desliza hacia la izquierda y la entrante ingresa por la derecha con aceleración/desaceleración *smoothstep*.
- **Haz de Energía Neón Láser:** Una línea vertical cian y blanca separa las escenas con resplandor difuminado y destello sutil de impacto.
- **SFX Sincronizado:** Efecto sonoro de barrido cinemático (*whoosh*) sintetizado e integrado en la pista de audio.
- **Misma Transición Consistente:** Se utiliza idénticamente al pasar de la **Intro al Minijuego** y del **Minijuego a la Pantalla Final (Outro)**.

### 3. Minijuego de Adivinanza (3 rondas x 14.5s = 43.5s)
| Ventana de Tiempo (por ronda) | Fase de Puntuación | Experiencia Visual y Sonora |
| :--- | :--- | :--- |
| **0.0s – 4.0s** | **Fase 1: +3 PUNTOS** | Pixelado retro alto (35px). Misterio total. Sonido sutil de tic-tac de reloj analógico. HUD dorado. |
| **4.0s – 8.0s** | **Fase 2: +2 PUNTOS** | Pixelado medio (18px). Se revelan la silueta general y paleta de colores. HUD naranja neón. |
| **8.0s – 12.0s** | **Fase 3: +1 PUNTO** | Pixelado leve (8px). Cuenta atrás con beeps sonoros ascendentes y barra de tiempo agotándose. HUD magenta. |
| **12.0s – 14.5s** | **Revelación: 0 PUNTOS** | **Desenfoque al 0% (Full HD Nítido)**. Campana de alarma analógica y fanfarria. Cartel: `IT'S [NOMBRE]!` con su videojuego. |

### 4. Pantalla de Cierre Interactiva / Outro (47.0s – 50.5s)
- **Tarjeta de Puntuación:** *"HOW MANY POINTS DID YOU GET? DID YOU GET ALL 9 POINTS?"*
- **Llamada a Comentar:** *"Comment 1-9 below and challenge your friends!"*
- **Botones de Interacción:** Badges vectoriales antialiased de **LIKE**, **SHARE** y **FOLLOW**.
- **Gancho de Fidelización:** *"NEW VIDEO EVERY DAY!"*

---

## Instalación en 1 Clic Multiplataforma

Para instalar este proyecto en cualquier ordenador, servidor o VPS:

### En Windows:
Simplemente haz doble clic sobre:
```
setup.bat
```
*(O ejecuta en PowerShell: `powershell -ExecutionPolicy Bypass -File .\setup.ps1`)*

El instalador automático se encarga de:
1. Detectar e instalar **Python 3.12** si no está presente (vía `winget`).
2. Detectar e instalar **FFmpeg** si no está presente.
3. Crear todas las carpetas del proyecto (`Blurred_characters`, `assets`, `backgrounds`, `data`).
4. Instalar todas las librerías de `requirements.txt`.
5. Crear el archivo `.env` inicial.

Una vez instalado, puedes usar el menú interactivo haciendo doble clic en:
```
run.bat
```

### En Linux / macOS / Servidores VPS:
Ejecuta en tu terminal:
```bash
chmod +x setup.sh
./setup.sh
```

---

## Comandos de Terminal (CLI)

Puedes ejecutar el generador directamente desde la consola:

### 1. Generar 1 video (3 personajes) de inmediato
```powershell
python main.py --once
```
*Selecciona automáticamente los siguientes 3 personajes del catálogo en rotación y renderiza el video completo de 50.5s.*

### 2. Iniciar el modo automático cada 4 horas
```powershell
python main.py --schedule
```
*Genera un video inmediatamente y después programa uno nuevo cada 4 horas de forma indefinida.*

### 3. Generar con personajes específicos
```powershell
python main.py --character mario,sonic,kratos --once
```
*Combina cualquiera de los más de 210 personajes icónicos del catálogo.*

### 4. Consultar el catálogo de personajes y su estado
```powershell
python main.py --list-characters
```

---

## Conexión con YouTube Shorts y TikTok

Los videos siempre se generarán y quedarán guardados en `Blurred_characters/`. Cuando desees activar la subida directa:

### YouTube Shorts:
1. Ve a [Google Cloud Console](https://console.cloud.google.com/) y crea un proyecto.
2. Habilita la **YouTube Data API v3**.
3. En *Credenciales*, crea un **ID de cliente de OAuth** (tipo *Aplicación de escritorio*).
4. Descarga el archivo JSON y colócalo en la raíz del proyecto como `client_secret.json`.
5. La primera vez que el bot suba a YouTube, abrirá una ventana de navegador para iniciar sesión en tu canal. Después guardará el token en `youtube_token.json` para todas las subidas automáticas futuras.

### TikTok:
1. Copia `.env.example` a un nuevo archivo `.env`:
 ```powershell
 copy .env.example .env
 ```
2. Introduce tu token de acceso en `TIKTOK_ACCESS_TOKEN`.

---

## Catálogo de 210+ Personajes Verificados

La base de datos en `data/characters.json` cuenta con **más de 210 personajes seleccionados**:
- **73 luchadores de Super Smash Bros Ultimate** con renders transparentes directos en alta resolución.
- **50 Pokémon** de múltiples generaciones.
- **87 Leyendas de Videojuegos Multiplataforma** (Kratos, Master Chief, Solid Snake, Geralt de Rivia, Doom Slayer, Gordon Freeman, Lara Croft, Arthur Morgan, etc.).

Si un personaje no dispone de imagen local en `assets/characters/`, el sistema descarga automáticamente el render oficial en alta resolución desde Wikipedia o el CDN de GitHub.

---

## Estructura del Proyecto

```
CharacterQuiz/
│
├── Blurred_characters/ # Carpeta de salida para videos MP4 generados y metadatos JSON
├── backgrounds/ # 24+ fondos temáticos de videojuegos con adaptación automática y viñeteado
├── assets/
│ ├── characters/ # Imágenes de personajes PNG transparentes en alta resolución
│ └── audio/
│ ├── bgm/ # Bandas sonoras chiptune / 16-bit RPG con licencia CC0 libre de copyright
│ └── sfx/ # Tic-tacs de reloj analógico, beeps, campana de revelación, whoosh
│
├── data/
│ ├── characters.json # Base de datos de más de 210 personajes con juego y etiquetas
│ └── history.json # Historial de rotación persistente para evitar repeticiones
│
├── src/
│ ├── config.py # Configuración central (resolución, FPS, intervalos, tiempos de ronda)
│ ├── character_manager.py # Gestión de rotación y descarga dinámica de Wikipedia / CDN
│ ├── audio_engine.py # Sintetizador procedural 44.1kHz en NumPy y mezclador de audio CC0
│ ├── video_generator.py # Motor de renderizado con pixelado progresivo, intro, transiciones y MoviePy 2.0
│ ├── scheduler.py # Demonio de programación en segundo plano cada 4 horas
│ └── uploaders/
│ ├── youtube_uploader.py # Integración con YouTube Data API v3 (#Shorts)
│ ├── tiktok_uploader.py # Integración con TikTok Content Posting API v2
│ └── manager.py # Despachador de subidas y registro de estado
│
├── .env.example # Plantilla de variables de entorno
├── requirements.txt # Dependencias de paquetes de Python
├── setup.bat / setup.ps1 # Instaladores automáticos de 1 clic para Windows
├── setup.sh # Instalador automático para Linux / macOS
├── run.bat # Menú interactivo de ejecución en Windows
├── main.py # Punto de entrada principal CLI
├── PORTFOLIO.md # Caso de estudio y guía técnica de portfolio (Inglés)
├── PORTFOLIO_es.md # Caso de estudio y guía técnica de portfolio (Español)
├── README.md # Documentación en inglés
└── README_es.md # Documentación en español
```
