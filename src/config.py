import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno si existe .env
load_dotenv()

# Rutas base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Carpeta obligatoria solicitada por el usuario en la raíz
OUTPUT_DIR = BASE_DIR / "Blurred_characters"
OUTPUT_DIR.mkdir(exist_ok=True)

# Rutas de assets y datos
ASSETS_DIR = BASE_DIR / "assets"
CHARACTERS_IMG_DIR = ASSETS_DIR / "characters"
AUDIO_DIR = ASSETS_DIR / "audio"
BGM_DIR = AUDIO_DIR / "bgm"
# Carpeta de fondos en la raíz del proyecto (Background o backgrounds)
if (BASE_DIR / "Background").exists():
    BACKGROUNDS_DIR = BASE_DIR / "Background"
elif (BASE_DIR / "backgrounds").exists():
    BACKGROUNDS_DIR = BASE_DIR / "backgrounds"
else:
    BACKGROUNDS_DIR = BASE_DIR / "Background"
    BACKGROUNDS_DIR.mkdir(parents=True, exist_ok=True)

DATA_DIR = BASE_DIR / "data"

CHARACTERS_FILE = DATA_DIR / "characters.json"
HISTORY_FILE = DATA_DIR / "history.json"

# Asegurar directorios
for directory in [CHARACTERS_IMG_DIR, AUDIO_DIR, BGM_DIR, DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuración del Video (Formato Vertical 9:16 para TikTok y YouTube Shorts)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30

# Estructura Multi-Personaje (Intro + 3 personajes + Outro con transiciones)
CHARACTERS_PER_VIDEO = 3
INTRO_DURATION = 2.5       # Pantalla de introducción inicial en segundos
TRANSITION_DURATION = 0.5  # Duración de cada transición (Intro -> Juego y Juego -> Outro)
ROUND_DURATION = 14.5      # 12.0s de adivinanza (4s por fase) + 2.5s de revelación
OUTRO_DURATION = 3.5       # Pantalla final de llamada a la acción en segundos
VIDEO_DURATION = (
    INTRO_DURATION +
    TRANSITION_DURATION +
    (ROUND_DURATION * CHARACTERS_PER_VIDEO) +
    TRANSITION_DURATION +
    OUTRO_DURATION
)  # 50.5s en total (ideal para formato Shorts/TikTok < 60s)

# Fases de puntuación y pixelado por ronda (en segundos de 0.0 a 14.5)
PHASE_3PTS_END = 4.0       # 0.0s - 4.0s: Pixelado alto -> 3 PUNTOS
PHASE_2PTS_END = 8.0       # 4.0s - 8.0s: Pixelado medio -> 2 PUNTOS
PHASE_1PTO_END = 12.0      # 8.0s - 12.0s: Pixelado leve -> 1 PUNTO
ROUND_REVEAL_START = 12.0  # 12.0s - 14.5s: Revelación nítida + alarma tradicional -> 0 PUNTOS

# Programación de subidas automáticas (cada 4 horas)
SCHEDULE_INTERVAL_HOURS = int(os.getenv("SCHEDULE_INTERVAL_HOURS", 4))

# Credenciales de API (opcionales, cargadas de .env)
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", str(BASE_DIR / "client_secret.json"))
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "")
