import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Configurar salida UTF-8 en Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from moviepy import VideoClip, AudioFileClip

from .config import (
    OUTPUT_DIR,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_FPS,
    VIDEO_DURATION,
    PHASE_1_END,
    PHASE_2_END,
    PHASE_3_END,
    REVEAL_START
)
from .audio_engine import AudioEngine

class VideoGenerator:
    def __init__(self):
        self.width = VIDEO_WIDTH
        self.height = VIDEO_HEIGHT
        self.fps = VIDEO_FPS
        self.duration = VIDEO_DURATION
        self.audio_engine = AudioEngine()
        self._load_fonts()

    def _load_fonts(self):
        """Carga fuentes legibles y de alto impacto para formato móvil."""
        font_candidates = [
            ("title", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 58),
            ("subtitle", ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/impact.ttf"], 32),
            ("clue_title", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 44),
            ("clue_body", ["C:/Windows/Fonts/arialbd.ttf"], 36),
            ("countdown", ["C:/Windows/Fonts/impact.ttf"], 130),
            ("reveal_name", ["C:/Windows/Fonts/impact.ttf"], 68),
            ("reveal_game", ["C:/Windows/Fonts/arialbd.ttf"], 38),
            ("badge", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 26),
            ("cta", ["C:/Windows/Fonts/arialbd.ttf"], 30)
        ]

        self.fonts = {}
        for key, paths, size in font_candidates:
            loaded = False
            for path in paths:
                if os.path.exists(path):
                    try:
                        self.fonts[key] = ImageFont.truetype(path, size)
                        loaded = True
                        break
                    except Exception:
                        pass
            if not loaded:
                self.fonts[key] = ImageFont.load_default()

    def _create_background(self):
        """Genera un fondo gamer con degradado oscuro y cuadrícula de neón sutil."""
        bg = Image.new("RGB", (self.width, self.height), (12, 14, 24))
        draw = ImageDraw.Draw(bg)

        # Gradiente radial central
        center_x, center_y = self.width // 2, self.height // 2
        for r in range(800, 0, -40):
            alpha = int(30 * (1 - r / 800))
            color = (16 + alpha, 20 + alpha, 42 + alpha * 2)
            draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], fill=color)

        # Cuadrícula sutil
        grid_color = (25, 30, 52)
        for y in range(0, self.height, 80):
            draw.line([(0, y), (self.width, y)], fill=grid_color, width=1)
        for x in range(0, self.width, 80):
            draw.line([(x, 0), (x, self.height)], fill=grid_color, width=1)

        return bg

    def _prepare_character_stages(self, image_path):
        """
        Prepara las versiones de la imagen con distintos niveles de difuminado.
        Utiliza un fondo de foco radial para resaltar cualquier silueta.
        """
        raw_img = Image.open(image_path).convert("RGBA")

        # Lienzo de 700x700 con foco radial de contraste
        box_size = 700
        base = Image.new("RGBA", (box_size, box_size), (15, 18, 30, 255))
        draw = ImageDraw.Draw(base)

        # Foco de luz ambiental en el centro para dar contraste al personaje
        cx, cy = box_size // 2, box_size // 2
        for r in range(320, 0, -20):
            factor = (1 - r / 320)
            glow_c = (int(35 + factor * 45), int(45 + factor * 55), int(75 + factor * 80), 255)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=glow_c)

        # Ajustar manteniendo proporción dentro de 640x640
        target_size = 640
        raw_img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)

        offset_x = (box_size - raw_img.width) // 2
        offset_y = (box_size - raw_img.height) // 2
        base.paste(raw_img, (offset_x, offset_y), raw_img)

        # Convertir a RGB para aplicar filtros de difuminado
        base_rgb = base.convert("RGB")

        # Generar las 4 fases de difuminado
        stage_1 = base_rgb.filter(ImageFilter.GaussianBlur(radius=65)) # Difuminado alto
        stage_2 = base_rgb.filter(ImageFilter.GaussianBlur(radius=30)) # Difuminado medio
        stage_3 = base_rgb.filter(ImageFilter.GaussianBlur(radius=12)) # Difuminado ligero
        stage_4 = base_rgb                                            # 100% nítido

        return {
            "stage_1": stage_1,
            "stage_2": stage_2,
            "stage_3": stage_3,
            "stage_4": stage_4
        }

    def _draw_text_with_outline(self, draw, pos, text, font, fill_color, outline_color=(0, 0, 0), outline_width=3, anchor="mm"):
        """Dibuja texto centrado con borde de alto contraste para máxima legibilidad."""
        draw.text(
            pos,
            text,
            font=font,
            fill=fill_color,
            stroke_width=outline_width,
            stroke_fill=outline_color,
            anchor=anchor
        )

    def generate_video(self, character, output_file=None):
        """Genera el video completo y su archivo de metadatos asociado."""
        start_time = time.time()
        char_id = character["id"]
        char_name = character["name"]
        game_name = character.get("game", "")
        clues = character.get("clues", ["¿De qué videojuego es este personaje?"])

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_file is None:
            output_file = OUTPUT_DIR / f"quiz_{timestamp_str}_{char_id}.mp4"
        else:
            output_file = Path(output_file)

        metadata_file = output_file.with_suffix(".json")

        print("\n" + "="*45)
        print(f"🎬 Generando Video para: {char_name} ({game_name})")
        print(f"📁 Salida: {output_file}")
        print("="*45)

        # 1. Preparar audio
        soundtrack_path = self.audio_engine.get_or_create_soundtrack(duration=self.duration)
        audio_clip = AudioFileClip(soundtrack_path)

        # 2. Preparar fondo e imágenes de personaje
        bg_static = self._create_background()
        char_stages = self._prepare_character_stages(character["image_path"])

        # Coordenadas del marco del personaje (centrado horizontalmente)
        card_w, card_h = 740, 740
        card_x = (self.width - card_w) // 2
        card_y = 350

        # Función generadora de cuadros por segundo
        def make_frame(t):
            frame = bg_static.copy()
            draw = ImageDraw.Draw(frame)

            # --- A. ENCABEZADO SUPERIOR ---
            draw.rounded_rectangle(
                [card_x, 150, card_x + card_w, 305],
                radius=25,
                fill=(20, 25, 45, 240),
                outline=(0, 240, 255),
                width=4
            )
            self._draw_text_with_outline(
                draw,
                (self.width // 2, 205),
                "¿QUIÉN ES ESTE PERSONAJE?",
                self.fonts["title"],
                fill_color=(255, 225, 0),
                outline_width=4
            )
            self._draw_text_with_outline(
                draw,
                (self.width // 2, 265),
                "[ ADIVINA EL VIDEOJUEGO ]",
                self.fonts["subtitle"],
                fill_color=(0, 240, 255),
                outline_width=3
            )

            # --- B. IMAGEN DEL PERSONAJE Y MARCO DE DIFUMINADO ---
            if t < PHASE_1_END:
                current_img = char_stages["stage_1"]
                border_color = (255, 60, 100) # Rosa misterio
                stage_label = "DIFUMINADO 100%"
            elif t < PHASE_2_END:
                current_img = char_stages["stage_2"]
                border_color = (255, 170, 0) # Naranja
                stage_label = "DIFUMINADO 50%"
            elif t < PHASE_3_END:
                current_img = char_stages["stage_3"]
                border_color = (0, 240, 255) # Cyan
                stage_label = "DIFUMINADO 20%"
            else:
                current_img = char_stages["stage_4"]
                border_color = (50, 255, 120) # Verde victoria
                stage_label = "¡REVELADO!"

            # Marco exterior con bordes redondeados
            draw.rounded_rectangle(
                [card_x - 10, card_y - 10, card_x + card_w + 10, card_y + card_h + 10],
                radius=28,
                fill=(14, 18, 30),
                outline=border_color,
                width=6
            )

            # Pegar imagen del personaje
            frame.paste(current_img, (card_x + 20, card_y + 20))

            # Insignia de estado en esquina superior (con margen adecuado)
            badge_w, badge_h = 250, 46
            badge_x1 = card_x + card_w - badge_w - 20
            badge_y1 = card_y + 20
            draw.rounded_rectangle(
                [badge_x1, badge_y1, badge_x1 + badge_w, badge_y1 + badge_h],
                radius=14,
                fill=(10, 12, 20),
                outline=border_color,
                width=2
            )
            self._draw_text_with_outline(
                draw,
                (badge_x1 + badge_w // 2, badge_y1 + badge_h // 2),
                stage_label,
                self.fonts["badge"],
                fill_color=border_color,
                outline_width=2
            )

            # --- C. SECCIÓN DE PISTAS / CUENTA ATRÁS / REVELACIÓN ---
            hud_y1 = 1130
            hud_h = 265
            hud_y2 = hud_y1 + hud_h

            if t < PHASE_1_END:
                # Pista 1: Apertura
                draw.rounded_rectangle(
                    [card_x, hud_y1, card_x + card_w, hud_y2],
                    radius=22,
                    fill=(20, 24, 42),
                    outline=(255, 60, 100),
                    width=3
                )
                self._draw_text_with_outline(
                    draw,
                    (self.width // 2, hud_y1 + 65),
                    ">> PISTA 1 <<",
                    self.fonts["clue_title"],
                    fill_color=(255, 220, 0)
                )
                self._draw_text_with_outline(
                    draw,
                    (self.width // 2, hud_y1 + 145),
                    "¿Reconoces los colores del personaje?",
                    self.fonts["clue_body"],
                    fill_color=(255, 255, 255)
                )
                self._draw_text_with_outline(
                    draw,
                    (self.width // 2, hud_y1 + 205),
                    "¡El difuminado se reducirá en 3 segundos!",
                    self.fonts["cta"],
                    fill_color=(170, 190, 230)
                )

            elif t < PHASE_2_END:
                # Pista 2: Pista temática
                clue_text = clues[0] if len(clues) > 0 else f"Aparece en la saga {game_name}"
                if len(clue_text) > 40:
                    words = clue_text.split(" ")
                    mid = len(words) // 2
                    line1 = " ".join(words[:mid])
                    line2 = " ".join(words[mid:])
                else:
                    line1 = clue_text
                    line2 = ""

                draw.rounded_rectangle(
                    [card_x, hud_y1, card_x + card_w, hud_y2],
                    radius=22,
                    fill=(20, 24, 42),
                    outline=(255, 170, 0),
                    width=3
                )
                self._draw_text_with_outline(
                    draw,
                    (self.width // 2, hud_y1 + 55),
                    ">> PISTA 2 <<",
                    self.fonts["clue_title"],
                    fill_color=(255, 200, 0)
                )
                self._draw_text_with_outline(
                    draw,
                    (self.width // 2, hud_y1 + 130),
                    line1,
                    self.fonts["clue_body"],
                    fill_color=(255, 255, 255)
                )
                if line2:
                    self._draw_text_with_outline(
                        draw,
                        (self.width // 2, hud_y1 + 185),
                        line2,
                        self.fonts["clue_body"],
                        fill_color=(255, 255, 255)
                    )

            elif t < REVEAL_START:
                # Cuenta atrás 3... 2... 1...
                draw.rounded_rectangle(
                    [card_x, hud_y1, card_x + card_w, hud_y2],
                    radius=22,
                    fill=(25, 20, 45),
                    outline=(0, 240, 255),
                    width=3
                )
                self._draw_text_with_outline(
                    draw,
                    (self.width // 2, hud_y1 + 50),
                    ">> ¡ÚLTIMOS SEGUNDOS! <<",
                    self.fonts["clue_title"],
                    fill_color=(0, 240, 255)
                )
                time_left = REVEAL_START - t
                num_display = str(max(1, int(time_left) + 1))
                self._draw_text_with_outline(
                    draw,
                    (self.width // 2, hud_y1 + 165),
                    num_display,
                    self.fonts["countdown"],
                    fill_color=(255, 40, 80),
                    outline_width=6
                )

            else:
                # FASE FINAL: ¡REVELACIÓN!
                draw.rounded_rectangle(
                    [card_x, hud_y1, card_x + card_w, hud_y2],
                    radius=22,
                    fill=(18, 42, 30),
                    outline=(50, 255, 120),
                    width=5
                )
                self._draw_text_with_outline(
                    draw,
                    (self.width // 2, hud_y1 + 60),
                    f">> ¡ES {char_name.upper()}! <<",
                    self.fonts["reveal_name"],
                    fill_color=(255, 230, 0),
                    outline_width=5
                )
                self._draw_text_with_outline(
                    draw,
                    (self.width // 2, hud_y1 + 140),
                    f"Saga: {game_name}",
                    self.fonts["reveal_game"],
                    fill_color=(255, 255, 255),
                    outline_width=3
                )
                self._draw_text_with_outline(
                    draw,
                    (self.width // 2, hud_y1 + 208),
                    "¿Lo adivinaste? ¡Comenta en qué segundo!",
                    self.fonts["cta"],
                    fill_color=(0, 255, 200),
                    outline_width=2
                )

            # --- D. BARRA DE TIEMPO (PROGRESS BAR) ---
            bar_w = card_w
            bar_h = 24
            bar_x1 = card_x
            bar_y1 = 1435
            draw.rounded_rectangle(
                [bar_x1, bar_y1, bar_x1 + bar_w, bar_y1 + bar_h],
                radius=12,
                fill=(10, 12, 20),
                outline=(50, 60, 90),
                width=2
            )
            if t < REVEAL_START:
                progress = max(0.0, min(1.0, 1.0 - (t / REVEAL_START)))
                fill_w = int(bar_w * progress)
                if fill_w > 10:
                    bar_color = (0, 240, 255) if progress > 0.3 else (255, 50, 80)
                    draw.rounded_rectangle(
                        [bar_x1, bar_y1, bar_x1 + fill_w, bar_y1 + bar_h],
                        radius=12,
                        fill=bar_color
                    )
            else:
                draw.rounded_rectangle(
                    [bar_x1, bar_y1, bar_x1 + bar_w, bar_y1 + bar_h],
                    radius=12,
                    fill=(255, 220, 0)
                )

            # --- E. LLAMADA A LA ACCIÓN INFERIOR (CTA) ---
            self._draw_text_with_outline(
                draw,
                (self.width // 2, 1550),
                ">> DALE LIKE Y COMPARTE CON TUS AMIGOS <<",
                self.fonts["subtitle"],
                fill_color=(255, 255, 255),
                outline_width=3
            )
            self._draw_text_with_outline(
                draw,
                (self.width // 2, 1610),
                ">> ¡SÍGUENOS PARA EL PRÓXIMO PERSONAJE! <<",
                self.fonts["subtitle"],
                fill_color=(0, 240, 255),
                outline_width=3
            )

            return np.array(frame)

        # 3. Renderizar video con MoviePy
        video_clip = VideoClip(make_frame, duration=self.duration)
        video_clip = video_clip.with_audio(audio_clip)

        video_clip.write_videofile(
            str(output_file),
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            bitrate="6000k",
            logger=None
        )

        video_clip.close()
        audio_clip.close()

        # 4. Generar metadatos para publicación
        tags = character.get("tags", ["#Shorts", "#Gaming", "#AdivinaElPersonaje"])
        hashtags_str = " ".join(tags)
        meta = {
            "title": f"¿Quién es este personaje? Adivina en los comentarios #Shorts",
            "description": f"¿Eres un auténtico gamer? Adivina qué personaje de videojuegos se esconde tras el difuminado.\n\nPersonaje: {char_name}\nSaga: {game_name}\n\n{hashtags_str}",
            "character_id": char_id,
            "character_name": char_name,
            "game": game_name,
            "video_path": str(output_file),
            "created_at": datetime.now().isoformat(),
            "tags": tags,
            "youtube_status": "READY_FOR_UPLOAD",
            "tiktok_status": "READY_FOR_UPLOAD"
        }
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        elapsed = time.time() - start_time
        print(f"Video renderizado con exito en {elapsed:.2f}s!")
        print(f"Metadatos guardados en: {metadata_file}\n")

        return output_file, meta
