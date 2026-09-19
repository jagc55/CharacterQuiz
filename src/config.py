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

# Estructura Multi-Personaje (3 personajes por video + Outro final)
CHARACTERS_PER_VIDEO = 3
ROUND_DURATION = 10.0  # Duración de cada ronda en segundos
OUTRO_DURATION = 3.5   # Pantalla final de llamada a la acción en segundos
VIDEO_DURATION = (ROUND_DURATION * CHARACTERS_PER_VIDEO) + OUTRO_DURATION  # 33.5s en total

# Fases de puntuación y pixelado por ronda (en segundos de 0.0 a 10.0)
PHASE_3PTS_END = 2.5       # 0.0s - 2.5s: Pixelado alto -> 3 PUNTOS
PHASE_2PTS_END = 5.0       # 2.5s - 5.0s: Pixelado medio -> 2 PUNTOS
PHASE_1PTO_END = 7.5       # 5.0s - 7.5s: Pixelado leve -> 1 PUNTO
ROUND_REVEAL_START = 7.5   # 7.5s - 10.0s: Revelación nítida -> 0 PUNTOS (Tiempo finalizado)

# Programación de subidas automáticas (cada 4 horas)
SCHEDULE_INTERVAL_HOURS = int(os.getenv("SCHEDULE_INTERVAL_HOURS", 4))

# Credenciales de API (opcionales, cargadas de .env)
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", str(BASE_DIR / "client_secret.json"))
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "")
