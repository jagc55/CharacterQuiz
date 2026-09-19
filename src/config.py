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
DATA_DIR = BASE_DIR / "data"

CHARACTERS_FILE = DATA_DIR / "characters.json"
HISTORY_FILE = DATA_DIR / "history.json"

# Asegurar directorios
for directory in [CHARACTERS_IMG_DIR, AUDIO_DIR, DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuración del Video (Formato Vertical 9:16 para TikTok y YouTube Shorts)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
VIDEO_DURATION = 13.0  # Duración óptima para retención y viralidad

# Fases del video en segundos
PHASE_1_END = 3.5    # Difuminado muy alto (100% misterio)
PHASE_2_END = 6.5    # Difuminado medio (50%, primera pista)
PHASE_3_END = 9.0    # Difuminado suave (cuenta atrás 3, 2, 1)
REVEAL_START = 9.0   # Revelación nítida (0% difuminado)

# Programación de subidas automáticas (cada 4 horas)
SCHEDULE_INTERVAL_HOURS = int(os.getenv("SCHEDULE_INTERVAL_HOURS", 4))

# Credenciales de API (opcionales, cargadas de .env)
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", str(BASE_DIR / "client_secret.json"))
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "")
