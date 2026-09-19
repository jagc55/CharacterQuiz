import sys
import json
import random
import requests
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from io import BytesIO

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
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

            # VALIDAR QUE EL CANDIDATO TENGA UN RECORTE LIMPIO Y AUTÉNTICO (TRANSPARENTE)
            has_cutout = self._ensure_character_image(chosen)
            if not has_cutout:
                # Si falló la descarga o es una captura cuadrada con fondo opaco, descartar
                if chosen in available:
                    available.remove(chosen)
                continue

            selected.append(chosen)
            selected_ids.add(chosen["id"])
            if chosen in available:
                available.remove(chosen)

        return selected

    def get_next_character(self, force_id=None):
        """Selecciona el siguiente personaje individual (compatibilidad hacia atrás)."""
        chars = self.get_next_characters(count=1, force_ids=[force_id] if force_id else None)
        return chars[0]

    def _get_pokemon_artwork(self, name):
        """Descarga el arte oficial transparente desde PokeAPI para personajes de Pokémon."""
        import re
        clean = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
        url = f"https://pokeapi.co/api/v2/pokemon/{clean}"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                art = r.json().get('sprites', {}).get('other', {}).get('official-artwork', {}).get('front_default')
                if art:
                    resp = requests.get(art, timeout=8)
                    if resp.status_code == 200 and len(resp.content) > 1500:
                        return Image.open(BytesIO(resp.content))
        except Exception:
            pass
        return None

    def _process_and_validate_cutout(self, pil_img, source_url=""):
        """
        Verifica exhaustivamente que la imagen sea un render auténticamente recortado con canal alfa transparente.
        - Descarta URLs con palabras clave de logos, portadas o capturas.
        - NUNCA aplica flood-fill ni recortes destructivos artificiales.
        - Exige canal alfa RGBA con transparencia real (>10% y <88%).
        - Verifica que el sujeto no sea un banner horizontal ni una marca de agua.
        - Recorta automáticamente márgenes transparentes vacíos (autocrop) para centrar al personaje.
        """
        if source_url:
            url_lower = source_url.lower()
            for bad_kw in ["logo", "cover", "boxart", "box_art", "poster", "soundtrack", "title_screen", "banner", "screenshot"]:
                if bad_kw in url_lower:
                    return None, False, f"URL contiene palabra vetada ({bad_kw})"

        rgba = pil_img.convert("RGBA")
        arr = np.array(rgba)
        h, w = arr.shape[:2]
        alpha = arr[:, :, 3]

        non_trans = alpha > 40
        trans_ratio = float(np.mean(~non_trans))

        # 1. Si no tiene píxeles visibles o está casi completamente vacía
        if not np.any(non_trans):
            return None, False, "Imagen completamente vacía / transparente"
        if trans_ratio > 0.88:
            return None, False, f"Sujeto minúsculo ({trans_ratio:.1%} transparente)"

        # 2. Si es una captura opaca (screenshot o fondo sólido sin canal alfa), RECHAZAR inmediatamente
        # NUNCA intentar flood-fill para no mutilar al personaje
        if trans_ratio < 0.10:
            return None, False, f"Imagen opaca sin canal alfa nativo ({trans_ratio:.1%})"

        # 3. Verificación de Bounding Box y Relación de Aspecto
        y_indices, x_indices = np.where(non_trans)
        min_y, max_y = np.min(y_indices), np.max(y_indices)
        min_x, max_x = np.min(x_indices), np.max(x_indices)
        sub_w = max_x - min_x
        sub_h = max_y - min_y

        if sub_h < 0.25 * h:
            return None, False, f"Sujeto demasiado plano ({sub_h}/{h} px)"

        aspect = sub_w / max(1, sub_h)
        if aspect > 1.50:
            return None, False, f"Sujeto horizontal tipo banner/logo (aspecto={aspect:.2f})"

        # 4. Ajustar recorte a los límites reales del sujeto (sin espacios vacíos sobrantes)
        cropped_img = rgba.crop((min_x, min_y, max_x + 1, max_y + 1))

        return cropped_img, True, f"Recorte auténtico (trans={trans_ratio:.1%}, aspect={aspect:.2f})"

    def _ensure_character_image(self, character):
        """
        Descarga y valida la imagen del personaje.
        Prioridad 1: 'render_url' verificado (Smash Ultimate, Wikimedia renders limpios, etc.).
        Prioridad 2: PokeAPI oficial para Pokémon.
        Prioridad 3: Wikipedia con filtro estricto anti-logos y anti-screenshots.
        Garantiza que NUNCA se utilicen imágenes equivocadas ni recortes erróneos.
        """
        char_id = character["id"]
        local_path = CHARACTERS_IMG_DIR / f"{char_id}.png"

        # Si ya existe en disco y es un recorte válido
        if local_path.exists() and local_path.stat().st_size > 1500:
            try:
                img = Image.open(local_path).convert("RGBA")
                cutout_img, is_valid, reason = self._process_and_validate_cutout(img)
                if is_valid:
                    character["image_path"] = str(local_path)
                    return True
                else:
                    local_path.unlink(missing_ok=True)
            except Exception:
                pass

        headers = {
            "User-Agent": "CharacterQuizBot/1.0 (gaming.quiz.bot@gmail.com)"
        }

        # 1. FUENTE PRIMARIA: 'render_url' directo y pre-verificado
        render_url = character.get("render_url")
        if render_url:
            try:
                resp = requests.get(render_url, headers=headers, timeout=10)
                if resp.status_code == 200 and len(resp.content) > 1500:
                    raw_img = Image.open(BytesIO(resp.content))
                    cutout_img, is_valid, reason = self._process_and_validate_cutout(raw_img, render_url)
                    if is_valid:
                        cutout_img.save(local_path, "PNG")
                        character["image_path"] = str(local_path)
                        try:
                            print(f"[OK] Render oficial verificado para {character['name']}")
                        except Exception:
                            pass
                        return True
            except Exception as e:
                try:
                    print(f"Aviso: Error en render_url de {character['name']}: {e}")
                except Exception:
                    pass

        # 2. FUENTE SECUNDARIA: PokeAPI oficial (para Pokémon)
        game_lower = character.get("game", "").lower()
        if "pokémon" in game_lower or "pokemon" in game_lower:
            poke_img = self._get_pokemon_artwork(character["name"])
            if poke_img:
                cutout_img, is_valid, reason = self._process_and_validate_cutout(poke_img, "https://pokeapi.co/official-artwork")
                if is_valid:
                    cutout_img.save(local_path, "PNG")
                    character["image_path"] = str(local_path)
                    try:
                        print(f"[OK] Arte oficial Ken Sugimori (PokeAPI) para {character['name']}")
                    except Exception:
                        pass
                    return True

        # 3. FUENTE TERCIARIA: Wikipedia (con exclusión estricta de páginas de juegos/secuelas)
        wiki_page = character.get("wiki_page")
        if wiki_page:
            # Si el nombre de la página de Wikipedia parece un juego o saga en lugar de un personaje, descartar
            wp_lower = wiki_page.lower()
            if any(k in wp_lower for k in ["_2", "_3", "_4", "_5", "_6", "_ii", "_iii", "_iv", "_v", "series", "franchise", "game"]):
                return False

            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_page}"
            try:
                resp = requests.get(url, headers=headers, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    thumb_url = data.get("thumbnail", {}).get("source")
                    if thumb_url:
                        clean_thumb_url = thumb_url.split("?")[0]
                        if not clean_thumb_url.lower().endswith(".png"):
                            return False

                        img_resp = requests.get(clean_thumb_url, headers=headers, timeout=12)
                        if img_resp.status_code == 200 and len(img_resp.content) > 1500:
                            raw_img = Image.open(BytesIO(img_resp.content))
                            cutout_img, is_valid, reason = self._process_and_validate_cutout(raw_img, clean_thumb_url)
                            if is_valid:
                                cutout_img.save(local_path, "PNG")
                                character["image_path"] = str(local_path)
                                try:
                                    print(f"[OK] Recorte validado para {character['name']}")
                                except Exception:
                                    pass
                                return True
            except Exception:
                pass

        return False

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
