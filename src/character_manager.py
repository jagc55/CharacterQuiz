import json
import random
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
        used = []
        for entry in self.history:
            if "character_id" in entry and entry["character_id"]:
                used.append(entry["character_id"])
            if "character_ids" in entry:
                used.extend(entry["character_ids"])
        return used

    def _get_franchise(self, character):
        """Obtiene la franquicia canónica del personaje para evitar repeticiones en el mismo video."""
        game_str = character.get("game", "")
        first_part = game_str.split("/")[0].strip().lower()
        keywords = [
            "mario", "zelda", "pokemon", "pokémon", "sonic", "final fantasy",
            "resident evil", "street fighter", "metal gear", "grand theft auto",
            "gta", "red dead", "last of us", "god of war", "halo", "crash",
            "spyro", "donkey kong", "kirby", "star fox", "metroid", "ratchet",
            "half-life", "tomb raider", "witcher", "doom", "hitman", "hollow knight",
            "undertale", "cuphead", "shovel knight", "rayman", "mortal kombat",
            "uncharted", "gears of war", "kingdom hearts", "ghost of tsushima",
            "horizon", "mega man", "devil may cry", "nier", "minecraft", "pac-man"
        ]
        for kw in keywords:
            if kw in first_part:
                return kw
        return first_part

    def _get_publisher(self, character):
        """Obtiene la compañía o plataforma principal (Nintendo, PlayStation, Xbox, Capcom, etc.)."""
        game_str = character.get("game", "")
        if "/" in game_str:
            return game_str.split("/")[-1].strip().lower()
        return "other"

    def get_next_characters(self, count=3, force_ids=None):
        """
        Selecciona 'count' personajes alternando obligatoriamente sus juegos y sagas.
        Garantiza que en un mismo video NUNCA coincidan dos personajes del mismo juego.
        Además, prioriza alternar entre distintas compañías y plataformas.
        """
        if not self.characters:
            raise ValueError("No hay personajes disponibles en data/characters.json")

        selected = []
        char_by_id = {c["id"]: c for c in self.characters}

        # Si se forzaron personajes por comando CLI (ej: --character mario,sonic,kratos)
        if force_ids:
            if isinstance(force_ids, str):
                force_ids = [fid.strip() for fid in force_ids.split(",") if fid.strip()]
            for fid in force_ids:
                if fid in char_by_id and char_by_id[fid] not in selected:
                    selected.append(char_by_id[fid])

        used_ids = set(self.get_used_character_ids())
        selected_ids = {c["id"] for c in selected}

        # Pool de personajes aún no utilizados en el historial
        available = [c for c in self.characters if c["id"] not in used_ids and c["id"] not in selected_ids]

        while len(selected) < count:
            selected_franchises = {self._get_franchise(c) for c in selected}
            selected_publishers = {self._get_publisher(c) for c in selected}

            # Si se acaban los no usados, reiniciar ciclo excluyendo los ya seleccionados en este video
            if not available:
                print("Todos los personajes han sido utilizados en el ciclo actual. Reiniciando ciclo...")
                available = [c for c in self.characters if c["id"] not in selected_ids]
                if not available:
                    break

            # 1. Filtrar candidatos cuya FRANQUICIA NO coincida con ninguna ya elegida en este video
            valid_candidates = [c for c in available if self._get_franchise(c) not in selected_franchises]

            # Si no quedan en el pool de no usados con distinta saga, buscar en todo el catálogo
            if not valid_candidates:
                fallback_pool = [c for c in self.characters if c["id"] not in selected_ids and self._get_franchise(c) not in selected_franchises]
                if fallback_pool:
                    valid_candidates = fallback_pool
                else:
                    valid_candidates = list(available)

            # 2. Priorizar candidatos que además provengan de una COMPAÑÍA/PLATAFORMA diferente
            ideal_candidates = [c for c in valid_candidates if self._get_publisher(c) not in selected_publishers]

            chosen = random.choice(ideal_candidates) if ideal_candidates else random.choice(valid_candidates)

            selected.append(chosen)
            selected_ids.add(chosen["id"])
            if chosen in available:
                available.remove(chosen)

        for char in selected:
            self._ensure_character_image(char)

        return selected

    def get_next_character(self, force_id=None):
        """Selecciona el siguiente personaje individual (compatibilidad hacia atrás)."""
        chars = self.get_next_characters(count=1, force_ids=[force_id] if force_id else None)
        return chars[0]

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

    def record_usage(self, character_ids, video_path, metadata=None):
        """Registra la creación del video en el historial para uno o varios personajes."""
        if isinstance(character_ids, str):
            character_ids = [character_ids]

        entry = {
            "character_id": character_ids[0] if character_ids else "",
            "character_ids": character_ids,
            "timestamp": datetime.now().isoformat(),
            "video_path": str(video_path),
            "youtube_status": metadata.get("youtube_status", "NOT_CONFIGURED") if metadata else "PENDING",
            "tiktok_status": metadata.get("tiktok_status", "NOT_CONFIGURED") if metadata else "PENDING"
        }
        self.history.append(entry)
        self._save_history()

    def cleanup_character_images(self, characters):
        """Elimina las imágenes de personajes descargadas para no ocupar espacio en disco."""
        import os
        if isinstance(characters, dict):
            characters = [characters]
        for c in characters:
            img_path = c.get("image_path")
            if img_path and os.path.exists(img_path):
                try:
                    os.remove(img_path)
                    print(f"[Cleanup] Imagen temporal eliminada para liberar espacio: {Path(img_path).name}")
                except Exception as e:
                    print(f"Aviso: No se pudo eliminar {img_path}: {e}")
