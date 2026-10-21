import os
import sys
import json
import time
import random
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
from PIL import Image, ImageDraw, ImageFont

from moviepy import VideoClip, AudioFileClip

from .config import (
    BASE_DIR,
    OUTPUT_DIR,
    BACKGROUNDS_DIR,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_FPS,
    VIDEO_DURATION,
    CHARACTERS_PER_VIDEO,
    INTRO_DURATION,
    TRANSITION_DURATION,
    ROUND_DURATION,
    OUTRO_DURATION,
    PHASE_3PTS_END,
    PHASE_2PTS_END,
    PHASE_1PTO_END,
    ROUND_REVEAL_START
)
from .audio_engine import AudioEngine
from .character_manager import CharacterManager

class VideoGenerator:
    def __init__(self):
        self.width = VIDEO_WIDTH
        self.height = VIDEO_HEIGHT
        self.fps = VIDEO_FPS
        self.duration = VIDEO_DURATION
        self.characters_per_video = CHARACTERS_PER_VIDEO
        self.intro_duration = INTRO_DURATION
        self.transition_duration = TRANSITION_DURATION
        self.round_duration = ROUND_DURATION
        self.outro_duration = OUTRO_DURATION
        self.audio_engine = AudioEngine()
        self._load_fonts()
        self._init_icons()

    def _load_fonts(self):
        """Carga fuentes modernas, legibles y de estilo gaming."""
        font_candidates = [
            ("title", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 50),
            ("round_badge", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 28),
            ("subtitle", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 36),
            ("hud_label", ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/impact.ttf"], 26),
            ("points_big", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 72),
            ("points_sub", ["C:/Windows/Fonts/arialbd.ttf"], 28),
            ("bar_text", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 28),
            ("reveal_name", ["C:/Windows/Fonts/impact.ttf"], 58),
            ("reveal_game", ["C:/Windows/Fonts/arialbd.ttf"], 34),
            ("badge", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 26),
            ("cta", ["C:/Windows/Fonts/arialbd.ttf"], 26),
            ("small", ["C:/Windows/Fonts/arialbd.ttf"], 22),
            ("outro_title", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 58),
            ("outro_card_title", ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/impact.ttf"], 30),
            ("outro_card_big", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 44),
            ("outro_card_huge", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 56),
            ("outro_card_sub", ["C:/Windows/Fonts/arialbd.ttf"], 24),
            ("outro_btn", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 30),
            # Fuentes especializadas para la pantalla de Introducción
            ("intro_huge", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 64),
            ("intro_title", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 52),
            ("intro_qmark", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 115),
            ("intro_card_title", ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/impact.ttf"], 32),
            ("intro_card_big", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 46),
            ("intro_card_sub", ["C:/Windows/Fonts/arialbd.ttf"], 25),
            ("intro_ready", ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"], 40)
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
        """
        Carga un fondo desde la carpeta Background o backgrounds en la raíz.
        Escala preservando la relación de aspecto (cover / center crop) a 1080x1920.
        Aplica un tinte suave y viñeteado periférico ligero para que el fondo
        del usuario luzca nítido y vibrante a la vez que la interfaz resalta.
        """
        valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        bg_files = []

        # Buscar en las variantes de la carpeta en la raíz (Background, backgrounds)
        for folder_name in ["Background", "backgrounds", "Backgrounds", "background"]:
            folder = BASE_DIR / folder_name
            if folder.exists() and folder.is_dir():
                for f in folder.glob("*.*"):
                    if f.suffix.lower() in valid_exts and f not in bg_files:
                        bg_files.append(f)

        if bg_files:
            chosen = random.choice(bg_files)
            try:
                base_img = Image.open(chosen).convert("RGBA")

                # Escalar manteniendo relación de aspecto sin deformar (cover)
                bw, bh = base_img.size
                scale = max(self.width / bw, self.height / bh)
                nw, nh = int(round(bw * scale)), int(round(bh * scale))
                resized = base_img.resize((nw, nh), Image.Resampling.LANCZOS)

                # Centrar y recortar a 1080x1920
                left = (nw - self.width) // 2
                top = (nh - self.height) // 2
                cropped = resized.crop((left, top, left + self.width, top + self.height))

                # Capa sutil de oscurecimiento suave (para garantizar máxima legibilidad de textos)
                overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 40))
                composite = Image.alpha_composite(cropped, overlay)

                # Viñeta suave en los extremos exteriores
                vignette = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
                v_draw = ImageDraw.Draw(vignette)
                cx, cy = self.width // 2, self.height // 2
                for r in range(1100, 750, -40):
                    alpha = int(24 * (1 - (r - 750) / 350))
                    v_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 0, 0, alpha))
                composite = Image.alpha_composite(composite, vignette)

                return composite.convert("RGB"), chosen.name
            except Exception as e:
                print(f"Aviso: Error cargando fondo {chosen.name} ({e}), usando fallback.")

        # Fallback si no se encuentran fondos
        bg = Image.new("RGB", (self.width, self.height), (14, 16, 26))
        draw = ImageDraw.Draw(bg)
        center_x, center_y = self.width // 2, self.height // 2
        for r in range(800, 0, -40):
            alpha = int(30 * (1 - r / 800))
            color = (16 + alpha, 20 + alpha, 42 + alpha * 2)
            draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], fill=color)

        return bg, "fallback_gradient"

    def _pixelate_image(self, img, block_size):
        """Aplica un efecto de pixelado estilo retro."""
        w, h = img.size
        small_w = max(1, w // block_size)
        small_h = max(1, h // block_size)
        small_img = img.resize((small_w, small_h), resample=Image.Resampling.BILINEAR)
        return small_img.resize((w, h), resample=Image.Resampling.NEAREST)

    def _prepare_character_stages(self, image_path):
        """
        Prepara las versiones de la imagen con distintos niveles de pixelado progresivo:
        - stage_1: Pixelado alto (~35px)  -> 3 PTS
        - stage_2: Pixelado medio (~18px) -> 2 PTS
        - stage_3: Pixelado leve (~8px)   -> 1 PTO
        - stage_4: Original 100% nítido   -> 0 PTS (¡REVELACIÓN!)
        """
        raw_img = Image.open(image_path).convert("RGBA")
        bbox = raw_img.getbbox()
        if bbox:
            raw_img = raw_img.crop(bbox)

        box_size = 700
        base = Image.new("RGBA", (box_size, box_size), (15, 18, 30, 255))
        draw = ImageDraw.Draw(base)

        cx, cy = box_size // 2, box_size // 2
        for r in range(320, 0, -20):
            factor = (1 - r / 320)
            glow_c = (int(35 + factor * 45), int(45 + factor * 55), int(75 + factor * 80), 255)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=glow_c)

        target_size = 640
        raw_img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)

        offset_x = (box_size - raw_img.width) // 2
        offset_y = (box_size - raw_img.height) // 2
        base.paste(raw_img, (offset_x, offset_y), raw_img)

        base_rgb = base.convert("RGB")

        stage_1 = self._pixelate_image(base_rgb, block_size=35)  # Máximo pixelado (3 pts)
        stage_2 = self._pixelate_image(base_rgb, block_size=18)  # Pixelado medio (2 pts)
        stage_3 = self._pixelate_image(base_rgb, block_size=8)   # Pixelado leve (1 pto)
        stage_4 = base_rgb                                      # 100% nítido (0 pts / revelado)

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

    def _init_icons(self):
        """Genera los iconos antialiased en alta resolución para los botones de interacción rápida."""
        self.icon_heart = self._make_heart_icon(34)
        self.icon_share = self._make_share_icon(34, (0, 240, 255))
        self.icon_follow = self._make_follow_icon(34, (50, 255, 130))

    def _make_heart_icon(self, size=34):
        s = size * 4
        hi = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(hi)
        r = int(s * 0.29)
        cx1 = int(s * 0.31)
        cx2 = int(s * 0.69)
        cy = int(s * 0.35)
        d.ellipse([cx1 - r, cy - r, cx1 + r, cy + r], fill=(255, 45, 100, 255))
        d.ellipse([cx2 - r, cy - r, cx2 + r, cy + r], fill=(255, 45, 100, 255))
        poly = [(int(s * 0.05), int(s * 0.42)), (int(s * 0.95), int(s * 0.42)), (int(s * 0.5), int(s * 0.94))]
        d.polygon(poly, fill=(255, 45, 100, 255))
        hr = int(r * 0.45)
        d.ellipse([cx1 - int(r*0.4) - hr, cy - int(r*0.3) - hr, cx1 - int(r*0.4) + hr, cy - int(r*0.3) + hr], fill=(255, 160, 190, 200))
        return hi.resize((size, size), Image.Resampling.LANCZOS)

    def _make_share_icon(self, size=34, color=(0, 240, 255)):
        s = size * 4
        si = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(si)
        arrowhead = [(int(s * 0.94), int(s * 0.20)), (int(s * 0.56), int(s * 0.12)), (int(s * 0.70), int(s * 0.36))]
        d.polygon(arrowhead, fill=color)
        arrowhead2 = [(int(s * 0.94), int(s * 0.20)), (int(s * 0.84), int(s * 0.58)), (int(s * 0.70), int(s * 0.36))]
        d.polygon(arrowhead2, fill=color)
        d.arc([int(s * 0.10), int(s * 0.36), int(s * 0.76), int(s * 0.94)], start=160, end=320, fill=color, width=int(s * 0.15))
        d.line([(int(s * 0.50), int(s * 0.42)), (int(s * 0.74), int(s * 0.28))], fill=color, width=int(s * 0.15))
        return si.resize((size, size), Image.Resampling.LANCZOS)

    def _make_follow_icon(self, size=34, color=(50, 255, 130)):
        s = size * 4
        fi = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(fi)
        hr = int(s * 0.19)
        hcx = int(s * 0.35)
        hcy = int(s * 0.32)
        d.ellipse([hcx - hr, hcy - hr, hcx + hr, hcy + hr], fill=color)
        tw = int(s * 0.33)
        d.chord([hcx - tw, int(s * 0.54), hcx + tw, int(s * 0.96)], start=180, end=360, fill=color)
        px = int(s * 0.78)
        py = int(s * 0.46)
        plen = int(s * 0.18)
        pw = int(s * 0.10)
        d.line([(px - plen, py), (px + plen, py)], fill=color, width=pw)
        d.line([(px, py - plen), (px, py + plen)], fill=color, width=pw)
        return fi.resize((size, size), Image.Resampling.LANCZOS)

    def _draw_intro_screen(self, frame, t_intro, num_rounds):
        """
        Dibuja la pantalla inicial de Introducción del video.
        TODO el texto está 100% en inglés:
        'CAN YOU GUESS THE FOLLOWING VIDEO GAME CHARACTERS?'
        Presenta las 3 rondas misteriosas, las reglas de puntos y la llamada a estar listos.
        Diseño gaming moderno con márgenes seguros para TikTok y Shorts.
        """
        draw = ImageDraw.Draw(frame)
        total_max_points = num_rounds * 3

        # --- A. TOP PILL: VIDEO GAME CHALLENGE ---
        pill_w, pill_h = 400, 52
        pill_x = (self.width - pill_w) // 2
        pill_y = 190
        draw.rounded_rectangle(
            [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
            radius=26,
            fill=(16, 20, 36, 230),
            outline=(0, 240, 255),
            width=2
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, pill_y + pill_h // 2),
            "VIDEO GAME CHALLENGE",
            self.fonts["round_badge"],
            fill_color=(0, 240, 255),
            outline_width=2
        )

        # --- B. MAIN HOOK TITLE (TEXTO EN INGLÉS REQUERIDO) ---
        self._draw_text_with_outline(
            draw,
            (self.width // 2, 285),
            "CAN YOU GUESS",
            self.fonts["intro_huge"],
            fill_color=(255, 255, 255),
            outline_color=(10, 15, 30),
            outline_width=5
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, 360),
            "THE FOLLOWING",
            self.fonts["intro_title"],
            fill_color=(0, 240, 255),
            outline_color=(10, 15, 30),
            outline_width=4
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, 435),
            "VIDEO GAME CHARACTERS?",
            self.fonts["intro_huge"],
            fill_color=(255, 215, 0),
            outline_color=(10, 15, 30),
            outline_width=5
        )

        # --- C. CARD 1: 3 MYSTERY ROUNDS & RULES ---
        card_w = 820
        card_x = (self.width - card_w) // 2
        card1_y = 520
        card1_h = 560

        draw.rounded_rectangle(
            [card_x, card1_y, card_x + card_w, card1_y + card1_h],
            radius=26,
            fill=(16, 20, 36),
            outline=(0, 240, 255),
            width=3
        )

        # 3 Mystery boxes inside Card 1
        box_w = 215
        box_h = 240
        box_gap = 20
        total_boxes_w = (3 * box_w) + (2 * box_gap)
        boxes_start_x = card_x + (card_w - total_boxes_w) // 2
        boxes_y = card1_y + 40

        mystery_boxes = [
            ("ROUND 1", (255, 215, 0)),
            ("ROUND 2", (0, 240, 255)),
            ("ROUND 3", (255, 55, 125))
        ]

        for i, (round_lbl, color) in enumerate(mystery_boxes):
            bx1 = boxes_start_x + i * (box_w + box_gap)
            bx2 = bx1 + box_w
            by1 = boxes_y
            by2 = by1 + box_h
            # Caja misteriosa oscura con borde neón
            draw.rounded_rectangle(
                [bx1, by1, bx2, by2],
                radius=20,
                fill=(22, 28, 48),
                outline=color,
                width=3
            )
            # Signo de interrogación '?' en negrita
            self._draw_text_with_outline(
                draw,
                ((bx1 + bx2) // 2, by1 + 95),
                "?",
                self.fonts["intro_qmark"],
                fill_color=color,
                outline_color=(10, 15, 30),
                outline_width=5
            )
            # Badge de la ronda en la parte inferior de la caja
            badge_h = 42
            draw.rounded_rectangle(
                [bx1 + 12, by2 - badge_h - 14, bx2 - 12, by2 - 14],
                radius=12,
                fill=(14, 18, 32),
                outline=color,
                width=2
            )
            self._draw_text_with_outline(
                draw,
                ((bx1 + bx2) // 2, by2 - 35),
                round_lbl,
                self.fonts["bar_text"],
                fill_color=color,
                outline_width=2
            )

        # Texto de reglas dentro de la Tarjeta 1
        self._draw_text_with_outline(
            draw,
            (self.width // 2, card1_y + 355),
            f"{num_rounds} CHARACTERS • {total_max_points} POINTS MAX",
            self.fonts["intro_card_title"],
            fill_color=(255, 215, 0),
            outline_width=3
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, card1_y + 420),
            "Guess before the pixels fully clear!",
            self.fonts["intro_card_sub"],
            fill_color=(200, 220, 250),
            outline_width=2
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, card1_y + 475),
            "The faster you guess, the more points you get!",
            self.fonts["intro_card_sub"],
            fill_color=(0, 240, 255),
            outline_width=2
        )

        # --- D. CARD 2: CHALLENGE CALLOUT ---
        card2_y = 1120
        card2_h = 270
        draw.rounded_rectangle(
            [card_x, card2_y, card_x + card_w, card2_y + card2_h],
            radius=24,
            fill=(16, 20, 36),
            outline=(50, 255, 130),
            width=3
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, card2_y + 55),
            "ARE YOU A TRUE GAMER?",
            self.fonts["intro_card_title"],
            fill_color=(255, 255, 255),
            outline_width=3
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, card2_y + 130),
            f"CAN YOU SCORE {total_max_points}/{total_max_points} POINTS?",
            self.fonts["intro_card_big"],
            fill_color=(50, 255, 130),
            outline_width=3
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, card2_y + 205),
            "Play along and comment your final score!",
            self.fonts["intro_card_sub"],
            fill_color=(200, 220, 250),
            outline_width=2
        )

        # --- E. BOTTOM READY BANNER ---
        banner_w, banner_h = 720, 80
        banner_x = (self.width - banner_w) // 2
        banner_y = 1435
        draw.rounded_rectangle(
            [banner_x, banner_y, banner_x + banner_w, banner_y + banner_h],
            radius=24,
            fill=(16, 20, 36, 230),
            outline=(255, 215, 0),
            width=3
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, banner_y + banner_h // 2),
            "GET READY TO PLAY!",
            self.fonts["intro_ready"],
            fill_color=(255, 215, 0),
            outline_color=(10, 12, 20),
            outline_width=3
        )

    def _draw_game_screen(self, frame, round_idx, round_t, char, char_stages, num_rounds):
        """
        Dibuja un frame individual del minijuego de adivinanza (Ronda activa).
        Incluye la tarjeta del personaje, fases de pixelado progresivo, temporizador y HUD.
        """
        draw = ImageDraw.Draw(frame)

        char_name = char["name"]
        raw_game_name = char.get("game", "")
        game_franchise = raw_game_name.split("/")[0].strip() if raw_game_name else "Video Game"

        card_w, card_h = 740, 740
        card_x = (self.width - card_w) // 2
        card_y = 280

        # --- A. TOP HEADER (CLEAN ENGLISH GAMING STYLE) ---
        pill_w, pill_h = 300, 48
        pill_x = (self.width - pill_w) // 2
        draw.rounded_rectangle(
            [pill_x, 120, pill_x + pill_w, 120 + pill_h],
            radius=24,
            fill=(16, 20, 36, 220),
            outline=(0, 240, 255),
            width=2
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, 144),
            f"ROUND {round_idx + 1} OF {num_rounds}",
            self.fonts["round_badge"],
            fill_color=(0, 240, 255),
            outline_width=2
        )

        self._draw_text_with_outline(
            draw,
            (self.width // 2, 215),
            "WHO IS THIS CHARACTER?",
            self.fonts["title"],
            fill_color=(255, 255, 255),
            outline_color=(10, 15, 30),
            outline_width=4
        )

        # --- B. PHASES OF PIXELATION AND POINTS ---
        if round_t < PHASE_3PTS_END:
            current_img = char_stages["stage_1"]
            border_color = (255, 215, 0)  # Bright Gold (3 pts)
            pts_label = "+3 POINTS"
            active_segment = 0
            phase_progress = round_t / PHASE_3PTS_END
        elif round_t < PHASE_2PTS_END:
            current_img = char_stages["stage_2"]
            border_color = (255, 145, 0)  # Neon Orange (2 pts)
            pts_label = "+2 POINTS"
            active_segment = 1
            phase_progress = (round_t - PHASE_3PTS_END) / (PHASE_2PTS_END - PHASE_3PTS_END)
        elif round_t < PHASE_1PTO_END:
            current_img = char_stages["stage_3"]
            border_color = (255, 55, 125)  # Arcade Magenta (1 pt)
            pts_label = "+1 POINT"
            active_segment = 2
            phase_progress = (round_t - PHASE_2PTS_END) / (PHASE_1PTO_END - PHASE_2PTS_END)
        else:
            current_img = char_stages["stage_4"]
            border_color = (50, 255, 130)  # Victory Green (Reveal / 0 pts)
            pts_label = "0 POINTS"
            active_segment = -1
            phase_progress = 1.0

        # --- C. CHARACTER CARD ---
        draw.rounded_rectangle(
            [card_x - 8, card_y - 8, card_x + card_w + 8, card_y + card_h + 8],
            radius=26,
            fill=(14, 18, 30),
            outline=border_color,
            width=5
        )
        frame.paste(current_img, (card_x + 20, card_y + 20))

        # --- D. CENTRAL HUD PANEL ---
        hud_y1 = 1055
        hud_h = 175
        hud_y2 = hud_y1 + hud_h

        if round_t < ROUND_REVEAL_START:
            # Guessing Phase
            draw.rounded_rectangle(
                [card_x, hud_y1, card_x + card_w, hud_y2],
                radius=20,
                fill=(16, 20, 36),
                outline=border_color,
                width=3
            )
            self._draw_text_with_outline(
                draw,
                (self.width // 2, hud_y1 + 52),
                "POINTS AT STAKE:",
                self.fonts["hud_label"],
                fill_color=(190, 210, 245),
                outline_width=2
            )
            self._draw_text_with_outline(
                draw,
                (self.width // 2, hud_y1 + 118),
                pts_label,
                self.fonts["points_big"],
                fill_color=border_color,
                outline_width=4
            )
        else:
            # Reveal Phase
            draw.rounded_rectangle(
                [card_x, hud_y1, card_x + card_w, hud_y2],
                radius=20,
                fill=(15, 36, 26),
                outline=(50, 255, 130),
                width=4
            )
            self._draw_text_with_outline(
                draw,
                (self.width // 2, hud_y1 + 54),
                f"IT'S {char_name.upper()}!",
                self.fonts["reveal_name"],
                fill_color=(255, 225, 0),
                outline_width=4
            )
            self._draw_text_with_outline(
                draw,
                (self.width // 2, hud_y1 + 122),
                f"Game: {game_franchise}",
                self.fonts["reveal_game"],
                fill_color=(255, 255, 255),
                outline_width=2
            )

        # --- E. SEGMENTED POINTS BAR ---
        bar_y1 = 1265
        bar_h = 56
        bar_y2 = bar_y1 + bar_h
        seg_gap = 12
        seg_w = (card_w - (2 * seg_gap)) // 3

        segments_info = [
            ("3 PTS", (255, 215, 0), (255, 255, 120)),
            ("2 PTS", (255, 145, 0), (255, 205, 80)),
            ("1 PT", (255, 55, 125), (255, 135, 185))
        ]

        for i, (label, color, glow) in enumerate(segments_info):
            seg_x1 = card_x + i * (seg_w + seg_gap)
            seg_x2 = seg_x1 + seg_w

            if active_segment == i:
                # ACTIVE segment
                draw.rounded_rectangle(
                    [seg_x1, bar_y1, seg_x2, bar_y2],
                    radius=14,
                    fill=color,
                    outline=glow,
                    width=3
                )
                sweep_w = int(seg_w * (1.0 - phase_progress))
                if sweep_w > 8:
                    draw.rounded_rectangle(
                        [seg_x1 + 4, bar_y2 - 8, seg_x1 + sweep_w - 4, bar_y2 - 3],
                        radius=3,
                        fill=(255, 255, 255)
                    )
                self._draw_text_with_outline(
                    draw,
                    ((seg_x1 + seg_x2) // 2, (bar_y1 + bar_y2) // 2 - 2),
                    label,
                    self.fonts["bar_text"],
                    fill_color=(10, 12, 20),
                    outline_color=(255, 255, 255),
                    outline_width=1
                )
            elif active_segment > i or active_segment == -1:
                # EXPIRED segment
                draw.rounded_rectangle(
                    [seg_x1, bar_y1, seg_x2, bar_y2],
                    radius=14,
                    fill=(18, 20, 30),
                    outline=(55, 60, 80),
                    width=1
                )
                self._draw_text_with_outline(
                    draw,
                    ((seg_x1 + seg_x2) // 2, (bar_y1 + bar_y2) // 2),
                    label,
                    self.fonts["bar_text"],
                    fill_color=(100, 105, 130),
                    outline_width=1
                )
            else:
                # UPCOMING segment
                draw.rounded_rectangle(
                    [seg_x1, bar_y1, seg_x2, bar_y2],
                    radius=14,
                    fill=(15, 18, 30),
                    outline=(color[0] // 3, color[1] // 3, color[2] // 3),
                    width=2
                )
                self._draw_text_with_outline(
                    draw,
                    ((seg_x1 + seg_x2) // 2, (bar_y1 + bar_y2) // 2),
                    label,
                    self.fonts["bar_text"],
                    fill_color=(color[0] // 2 + 60, color[1] // 2 + 60, color[2] // 2 + 60),
                    outline_width=1
                )

        # --- F. ROUND COUNTDOWN PROGRESS BAR ---
        pbar_y1 = 1345
        pbar_h = 14
        draw.rounded_rectangle(
            [card_x, pbar_y1, card_x + card_w, pbar_y1 + pbar_h],
            radius=7,
            fill=(12, 14, 24),
            outline=(45, 50, 75),
            width=1
        )
        if round_t < ROUND_REVEAL_START:
            prog = max(0.0, min(1.0, 1.0 - (round_t / ROUND_REVEAL_START)))
            fill_w = int(card_w * prog)
            if fill_w > 8:
                draw.rounded_rectangle(
                    [card_x, pbar_y1, card_x + fill_w, pbar_y1 + pbar_h],
                    radius=7,
                    fill=border_color
                )
        else:
            draw.rounded_rectangle(
                [card_x, pbar_y1, card_x + card_w, pbar_y1 + pbar_h],
                radius=7,
                fill=(50, 255, 130)
            )

        # --- G. BOTTOM QUESTION ---
        cta_w, cta_h = 680, 74
        cta_x = (self.width - cta_w) // 2
        cta_y = 1530
        draw.rounded_rectangle(
            [cta_x, cta_y, cta_x + cta_w, cta_y + cta_h],
            radius=22,
            fill=(16, 20, 36, 230),
            outline=(255, 215, 0),
            width=3
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, cta_y + cta_h // 2),
            f"CAN YOU GET {num_rounds * 3} POINTS?",
            self.fonts["subtitle"],
            fill_color=(255, 215, 0),
            outline_color=(10, 12, 20),
            outline_width=3
        )

    def _draw_outro_screen(self, frame, t_outro, num_rounds):
        """
        Dibuja la pantalla final de llamada a la acción (Outro):
        1. Pregunta cuántos puntos ha conseguido e invita a comentar.
        2. Llama a dar Like, Compartir y Seguir para no perderse los próximos videos.
        Diseño gaming moderno, limpio, centrado y con márgenes seguros para TikTok/Shorts.
        """
        draw = ImageDraw.Draw(frame)
        total_max_points = num_rounds * 3

        # --- A. TOP PILL: QUIZ COMPLETE! ---
        pill_w, pill_h = 360, 52
        pill_x = (self.width - pill_w) // 2
        pill_y = 190
        draw.rounded_rectangle(
            [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
            radius=26,
            fill=(16, 20, 36, 230),
            outline=(0, 240, 255),
            width=2
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, pill_y + pill_h // 2),
            "QUIZ COMPLETE!",
            self.fonts["round_badge"],
            fill_color=(0, 240, 255),
            outline_width=2
        )

        # --- B. MAIN TITLE ---
        self._draw_text_with_outline(
            draw,
            (self.width // 2, 290),
            "HOW MANY POINTS",
            self.fonts["outro_title"],
            fill_color=(255, 255, 255),
            outline_color=(10, 15, 30),
            outline_width=4
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, 360),
            "DID YOU GET?",
            self.fonts["outro_title"],
            fill_color=(255, 215, 0),
            outline_color=(10, 15, 30),
            outline_width=4
        )

        # --- C. CARD 1: COMMENTS CALLOUT ---
        card_w, card_h = 800, 220
        card_x = (self.width - card_w) // 2
        card1_y = 440
        draw.rounded_rectangle(
            [card_x, card1_y, card_x + card_w, card1_y + card_h],
            radius=24,
            fill=(16, 20, 36),
            outline=(0, 240, 255),
            width=3
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, card1_y + 48),
            "LEAVE A COMMENT WITH YOUR SCORE!",
            self.fonts["outro_card_title"],
            fill_color=(0, 240, 255),
            outline_width=2
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, card1_y + 115),
            f"DID YOU GET ALL {total_max_points} POINTS?",
            self.fonts["outro_card_big"],
            fill_color=(255, 215, 0),
            outline_width=3
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, card1_y + 175),
            f"Comment 1-{total_max_points} below and challenge your friends!",
            self.fonts["outro_card_sub"],
            fill_color=(200, 215, 240),
            outline_width=2
        )

        # --- D. ROW OF ACTION BUTTON BADGES WITH ICONS ---
        btn_w = 240
        btn_h = 68
        btn_gap = 18
        total_btns_w = (3 * btn_w) + (2 * btn_gap)
        btns_start_x = (self.width - total_btns_w) // 2
        btns_y = 695

        buttons = [
            ("LIKE", (255, 55, 125), (34, 14, 26), self.icon_heart),
            ("SHARE", (0, 240, 255), (12, 28, 38), self.icon_share),
            ("FOLLOW", (50, 255, 130), (12, 34, 22), self.icon_follow)
        ]

        for i, (label, color, fill_c, icon) in enumerate(buttons):
            bx1 = btns_start_x + i * (btn_w + btn_gap)
            bx2 = bx1 + btn_w
            draw.rounded_rectangle(
                [bx1, btns_y, bx2, btns_y + btn_h],
                radius=18,
                fill=fill_c,
                outline=color,
                width=3
            )

            bbox = self.fonts["outro_btn"].getbbox(label)
            tw = bbox[2] - bbox[0]
            gap = 12
            content_w = icon.width + gap + tw
            start_cx = bx1 + (btn_w - content_w) // 2
            icon_cy = btns_y + (btn_h - icon.height) // 2

            frame.paste(icon, (start_cx, icon_cy), icon)

            text_x = start_cx + icon.width + gap + (tw // 2)
            text_y = btns_y + (btn_h // 2)
            self._draw_text_with_outline(
                draw,
                (text_x, text_y),
                label,
                self.fonts["outro_btn"],
                fill_color=color,
                outline_width=2
            )

        # --- E. CARD 2: LIKE, SHARE & FOLLOW CALLOUT ---
        card2_y = 795
        card2_h = 260
        draw.rounded_rectangle(
            [card_x, card2_y, card_x + card_w, card2_y + card2_h],
            radius=24,
            fill=(16, 20, 36),
            outline=(50, 255, 130),
            width=3
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, card2_y + 55),
            "LIKE & SHARE THIS VIDEO!",
            self.fonts["outro_card_big"],
            fill_color=(255, 255, 255),
            outline_width=3
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, card2_y + 130),
            "FOLLOW US",
            self.fonts["outro_card_huge"],
            fill_color=(50, 255, 130),
            outline_width=4
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, card2_y + 205),
            "SO YOU DON'T MISS THE NEXT QUIZ!",
            self.fonts["outro_card_title"],
            fill_color=(255, 215, 0),
            outline_width=2
        )

        # --- F. BOTTOM PILL: NEW VIDEO EVERY DAY! ---
        banner_w, banner_h = 680, 74
        banner_x = (self.width - banner_w) // 2
        banner_y = 1090
        draw.rounded_rectangle(
            [banner_x, banner_y, banner_x + banner_w, banner_y + banner_h],
            radius=22,
            fill=(16, 20, 36, 230),
            outline=(255, 215, 0),
            width=3
        )
        self._draw_text_with_outline(
            draw,
            (self.width // 2, banner_y + banner_h // 2),
            "NEW VIDEO EVERY DAY!",
            self.fonts["subtitle"],
            fill_color=(255, 215, 0),
            outline_color=(10, 12, 20),
            outline_width=3
        )

    def _apply_transition(self, frame_from, frame_to, progress):
        """
        Aplica la transición cinemática estilo gaming (Push Slide con haz de energía neón cian/dorado).
        Se utiliza idénticamente para:
        1. Transición de Pantalla de Introducción -> Minijuego.
        2. Transición de Minijuego -> Pantalla Final (Outro).
        progress va de 0.0 a 1.0.
        """
        # Suavizado cúbico Hermite (smoothstep)
        p = max(0.0, min(1.0, progress))
        t = p * p * (3.0 - 2.0 * p)
        dx = int(self.width * t)

        # Lienzo combinado con desplazamiento fluido
        res = Image.new("RGBA", (self.width, self.height))
        res.paste(frame_from, (-dx, 0))
        res.paste(frame_to, (self.width - dx, 0))

        # Dibujar haz de energía láser / neón en la unión
        seam_x = self.width - dx
        beam_overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        bd = ImageDraw.Draw(beam_overlay)

        # Resplandor cian suave multiescala
        glow_half_width = 36
        for offset in range(-glow_half_width, glow_half_width + 1):
            x = seam_x + offset
            if 0 <= x < self.width:
                dist = abs(offset) / glow_half_width
                alpha = int(180 * ((1.0 - dist) ** 2))
                bd.line([(x, 0), (x, self.height)], fill=(0, 240, 255, alpha), width=1)

        # Núcleo brillante concentrado
        for offset in range(-4, 5):
            x = seam_x + offset
            if 0 <= x < self.width:
                dist = abs(offset) / 4.0
                alpha = int(240 * (1.0 - dist))
                bd.line([(x, 0), (x, self.height)], fill=(200, 250, 255, alpha), width=1)

        # Línea central blanca láser
        bd.line([(seam_x, 0), (seam_x, self.height)], fill=(255, 255, 255, 255), width=3)

        # Destello luminoso de impacto sutil en el punto medio (p = 0.5)
        flash_intensity = 1.0 - abs(p - 0.5) / 0.5
        if flash_intensity > 0.6:
            f_alpha = int(70 * ((flash_intensity - 0.6) / 0.4))
            bd.rectangle([0, 0, self.width, self.height], fill=(200, 245, 255, f_alpha))

        return Image.alpha_composite(res, beam_overlay).convert("RGB")

    def generate_video(self, characters, output_file=None):
        """
        Genera el video completo con:
        1. Pantalla de Introducción (100% en inglés: "CAN YOU GUESS THE FOLLOWING VIDEO GAME CHARACTERS?").
        2. Transición cinemática gaming (haz neón) al minijuego.
        3. Minijuego interactivo con 3 personajes, pixelado progresivo, puntos y SFX.
        4. Misma transición cinemática gaming a la pantalla final.
        5. Pantalla Outro con llamada a comentar puntuación, dar like, compartir y seguir.
        """
        start_time = time.time()

        if isinstance(characters, dict):
            characters = [characters]

        num_rounds = len(characters)
        intro_dur = self.intro_duration
        trans_dur = self.transition_duration
        minigame_dur = self.round_duration * num_rounds
        outro_dur = self.outro_duration

        # Puntos temporales clave en la línea de tiempo total
        t_intro_end = intro_dur
        t_trans1_end = t_intro_end + trans_dur
        t_minigame_end = t_trans1_end + minigame_dur
        t_trans2_end = t_minigame_end + trans_dur
        total_duration = t_trans2_end + outro_dur

        char_ids = [c["id"] for c in characters]
        char_names = [c["name"] for c in characters]
        game_names = [c.get("game", "") for c in characters]

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug_ids = "_".join(char_ids[:3])
        if output_file is None:
            output_file = OUTPUT_DIR / f"quiz_{timestamp_str}_{slug_ids}.mp4"
        else:
            output_file = Path(output_file)

        # Archivo temporal para garantizar escritura atómica segura y evitar archivos corruptos
        temp_output = output_file.with_name(f"{output_file.stem}_temp.mp4")
        metadata_file = output_file.with_suffix(".json")

        print("\n" + "="*58)
        print(f"🎮 Generando Video de Adivinanza (Intro + {num_rounds} Rondas + Outro + Transiciones)")
        print(f"  🎬 Intro: {intro_dur:.1f}s | Transiciones: 2x {trans_dur:.1f}s")
        for i, c in enumerate(characters, 1):
            print(f"  Ronda {i}: {c['name']} - {c.get('game', '')}")
        print(f"📁 Salida: {output_file.name}")
        print(f"⏱️ Duración Total: {total_duration:.1f}s")
        print("="*58)

        try:
            # 1. Preparar audio (música aesthetic sin copyright + SFX sincronizados)
            soundtrack_path = self.audio_engine.get_or_create_soundtrack(
                duration=total_duration,
                num_rounds=num_rounds,
                round_duration=self.round_duration,
                intro_duration=self.intro_duration,
                transition_duration=self.transition_duration
            )
            audio_clip = AudioFileClip(soundtrack_path)

            # 2. Pre-procesar etapas de pixelado y fondo del usuario
            bg_static, chosen_bg_name = self._create_background()
            print(f"🖼️ Fondo seleccionado: {chosen_bg_name}")
            all_char_stages = [self._prepare_character_stages(c["image_path"]) for c in characters]

            # 3. Pre-renderizar fotogramas base clave para optimizar la velocidad de las transiciones
            # Fotograma final de la intro para Transición 1
            trans1_from_frame = bg_static.copy()
            self._draw_intro_screen(trans1_from_frame, t_intro=intro_dur, num_rounds=num_rounds)

            # Fotograma inicial de la Ronda 1 para Transición 1
            trans1_to_frame = bg_static.copy()
            self._draw_game_screen(
                trans1_to_frame,
                round_idx=0,
                round_t=0.0,
                char=characters[0],
                char_stages=all_char_stages[0],
                num_rounds=num_rounds
            )

            # Fotograma final de la última ronda (revelación) para Transición 2
            trans2_from_frame = bg_static.copy()
            last_round_idx = num_rounds - 1
            self._draw_game_screen(
                trans2_from_frame,
                round_idx=last_round_idx,
                round_t=self.round_duration,
                char=characters[last_round_idx],
                char_stages=all_char_stages[last_round_idx],
                num_rounds=num_rounds
            )

            # Fotograma inicial del Outro para Transición 2
            trans2_to_frame = bg_static.copy()
            self._draw_outro_screen(trans2_to_frame, t_outro=0.0, num_rounds=num_rounds)

            # Generator function per frame
            def make_frame(t):
                # FASE 1: Pantalla de Introducción
                if t < t_intro_end:
                    frame = bg_static.copy()
                    self._draw_intro_screen(frame, t_intro=t, num_rounds=num_rounds)
                    return np.array(frame)

                # FASE 2: Transición 1 (Intro -> Minijuego)
                elif t < t_trans1_end:
                    progress = (t - t_intro_end) / trans_dur
                    trans_frame = self._apply_transition(trans1_from_frame, trans1_to_frame, progress)
                    return np.array(trans_frame)

                # FASE 3: Minijuego de Adivinanza (Rondas 1 a num_rounds)
                elif t < t_minigame_end:
                    t_game = t - t_trans1_end
                    round_idx = min(int(t_game // self.round_duration), num_rounds - 1)
                    round_t = t_game - (round_idx * self.round_duration)
                    frame = bg_static.copy()
                    self._draw_game_screen(
                        frame,
                        round_idx=round_idx,
                        round_t=round_t,
                        char=characters[round_idx],
                        char_stages=all_char_stages[round_idx],
                        num_rounds=num_rounds
                    )
                    return np.array(frame)

                # FASE 4: Transición 2 (Minijuego -> Pantalla Final Outro - MISMA TRANSICIÓN)
                elif t < t_trans2_end:
                    progress = (t - t_minigame_end) / trans_dur
                    trans_frame = self._apply_transition(trans2_from_frame, trans2_to_frame, progress)
                    return np.array(trans_frame)

                # FASE 5: Pantalla Final de Llamada a la Acción (Outro)
                else:
                    t_outro = t - t_trans2_end
                    frame = bg_static.copy()
                    self._draw_outro_screen(frame, t_outro=t_outro, num_rounds=num_rounds)
                    return np.array(frame)

            # 4. Render video with MoviePy displaying live progress bar
            print(f"\n⏳ Renderizando video en alta definición de {total_duration:.1f}s (progreso en tiempo real)...")
            video_clip = VideoClip(make_frame, duration=total_duration)
            video_clip = video_clip.with_audio(audio_clip)

            video_clip.write_videofile(
                str(temp_output),
                fps=self.fps,
                codec="libx264",
                audio_codec="aac",
                preset="ultrafast",
                bitrate="6000k",
                logger='bar'
            )

            video_clip.close()
            audio_clip.close()

            # Renombrar archivo temporal al destino final tras completar exitosamente
            if temp_output.exists():
                if output_file.exists():
                    output_file.unlink()
                temp_output.rename(output_file)

            # 5. Generar metadatos para publicación
            all_tags = set(["#Shorts", "#Gaming", "#GuessTheCharacter", "#GamerQuiz", "#GamingTrivia", "#PixelQuiz", "#VideoGames"])
            for c in characters:
                for tag in c.get("tags", []):
                    all_tags.add(tag)
            hashtags_str = " ".join(list(all_tags)[:12])

            char_list_str = "\n".join([f"Round {i+1}: {c['name']} ({c.get('game', '').split('/')[0].strip()})" for i, c in enumerate(characters)])

            meta = {
                "title": f"Can you guess these {num_rounds} video game characters? Gamer Quiz #Shorts",
                "description": f"Are you a true gamer? Guess the {num_rounds} characters hidden behind the pixels.\n\nMax score: {num_rounds * 3} Points (3 pts per character)\n\n{char_list_str}\n\n{hashtags_str}",
                "characters": [
                    {"id": c["id"], "name": c["name"], "game": c.get("game", "").split("/")[0].strip()}
                    for c in characters
                ],
                "character_id": characters[0]["id"] if characters else "",
                "character_ids": char_ids,
                "character_name": ", ".join(char_names),
                "game": ", ".join(game_names),
                "video_path": str(output_file),
                "background": chosen_bg_name,
                "created_at": datetime.now().isoformat(),
                "tags": list(all_tags),
                "youtube_status": "READY_FOR_UPLOAD",
                "tiktok_status": "READY_FOR_UPLOAD"
            }
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)

            elapsed = time.time() - start_time
            print(f"\n🎉 Video ({num_rounds} personajes + Intro + Transiciones + Outro) completado con éxito en {elapsed:.2f}s!")
            print(f"📁 Video final: {output_file}")
            print(f"📄 Metadatos: {metadata_file}\n")

            # 6. Limpieza automática de imágenes temporales para no saturar disco
            CharacterManager().cleanup_character_images(characters)

            return output_file, meta

        finally:
            if temp_output.exists():
                try:
                    temp_output.unlink()
                except Exception:
                    pass
