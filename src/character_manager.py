import json
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO
from datetime import datetime

from .config import CHARACTERS_FILE, HISTORY_FILE, CHARACTERS_IMG_DIR

class CharacterManager:
    def __init__(self):
        self.characters = self._load_characters()
        self.history = self._load_history()

    def _load_characters(self):
        if not CHARACTERS_FILE.exists():
            return []
        with open(CHARACTERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_history(self):
        if not HISTORY_FILE.exists():
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def get_used_character_ids(self):
        return [entry["character_id"] for entry in self.history if "character_id" in entry]

    def get_next_character(self, force_id=None):
        """Selecciona el siguiente personaje sin repetir hasta agotar la lista."""
        if not self.characters:
            raise ValueError("No hay personajes disponibles en data/characters.json")

        if force_id:
            for char in self.characters:
                if char["id"] == force_id:
                    self._ensure_character_image(char)
                    return char
            raise ValueError(f"Personaje con id '{force_id}' no encontrado.")

        used_ids = set(self.get_used_character_ids())
        available = [c for c in self.characters if c["id"] not in used_ids]

        # Si ya se usaron todos los personajes, reiniciamos el ciclo conservando el log
        if not available:
            print("Todos los personajes han sido utilizados. Reiniciando ciclo de selección...")
            available = self.characters

        selected = available[0]
        self._ensure_character_image(selected)
        return selected

    def _ensure_character_image(self, character):
        """Comprueba si la imagen existe localmente; si no, la descarga."""
        char_id = character["id"]
        local_path = CHARACTERS_IMG_DIR / f"{char_id}.png"

        if local_path.exists() and local_path.stat().st_size > 1000:
            character["image_path"] = str(local_path)
            return

        print(f"Descargando imagen para {character['name']}...")
        wiki_page = character.get("wiki_page")
        if not wiki_page:
            wiki_page = character["name"].replace(" ", "_")

        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_page}"
        headers = {"User-Agent": "CharacterQuizBot/1.0 (contacto@gamingquiz.local)"}

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                thumb_url = data.get("thumbnail", {}).get("source")
                if thumb_url:
                    # Intentar obtener versión de mayor resolución reemplazando el ancho en la URL si es de wikipedia
                    img_resp = requests.get(thumb_url, headers=headers, timeout=15)
                    if img_resp.status_code == 200:
                        img = Image.open(BytesIO(img_resp.content)).convert("RGBA")
                        img.save(local_path, "PNG")
                        print(f"Imagen guardada en {local_path}")
                        character["image_path"] = str(local_path)
                        return
        except Exception as e:
            print(f"Error descargando imagen de Wikipedia para {char_id}: {e}")

        # Si no se pudo descargar, creamos una tarjeta de imagen estética de respaldo
        self._create_fallback_image(character, local_path)
        character["image_path"] = str(local_path)

    def _create_fallback_image(self, character, output_path):
        """Crea una imagen estilizada si no se encuentra en línea."""
        from PIL import ImageDraw, ImageFont
        img = Image.new("RGBA", (700, 700), (20, 20, 35, 255))
        draw = ImageDraw.Draw(img)
        # Dibujar bordes de neón
        draw.rectangle([10, 10, 690, 690], outline=(0, 220, 255), width=6)
        draw.text((350, 320), character["name"], fill=(255, 255, 255), anchor="mm")
        img.save(output_path, "PNG")
        print(f"Imagen de respaldo creada para {character['name']}")

    def record_usage(self, character_id, video_path, metadata=None):
        """Registra la creación del video en el historial."""
        entry = {
            "character_id": character_id,
            "timestamp": datetime.now().isoformat(),
            "video_path": str(video_path),
            "youtube_status": metadata.get("youtube_status", "NOT_CONFIGURED") if metadata else "PENDING",
            "tiktok_status": metadata.get("tiktok_status", "NOT_CONFIGURED") if metadata else "PENDING"
        }
        self.history.append(entry)
        self._save_history()
