import os
import random
import wave
import numpy as np
from pathlib import Path
from moviepy import AudioFileClip, CompositeAudioClip
from .config import AUDIO_DIR, BGM_DIR, VIDEO_DURATION, CHARACTERS_PER_VIDEO, ROUND_DURATION

class AudioEngine:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def get_or_create_soundtrack(self, duration=VIDEO_DURATION, output_path=None, num_rounds=CHARACTERS_PER_VIDEO, round_duration=ROUND_DURATION):
        """
        Genera o mezcla la banda sonora sincronizada con el número de rondas.
        Utiliza música de videojuegos sin copyright (chiptune / 16-bit) desde assets/audio/bgm/
        y mezcla sobre ella los efectos de sonido de cuenta atrás y revelación.
        """
        if output_path is None:
            output_path = AUDIO_DIR / f"soundtrack_{num_rounds}rounds_{int(duration)}s.wav"
        else:
            output_path = Path(output_path)

        # 1. Buscar pistas de fondo en assets/audio/bgm/
        bgm_files = []
        if BGM_DIR.exists():
            bgm_files = [f for f in BGM_DIR.glob("*.*") if f.suffix.lower() in [".ogg", ".mp3", ".wav"]]

        # Si encontramos música de fondo auténtica, la mezclamos con los efectos de juego
        if bgm_files:
            try:
                selected_bgm = random.choice(bgm_files)
                print(f"🎵 Música de fondo seleccionada (sin copyright): {selected_bgm.name}")
                return self._mix_bgm_with_sfx(selected_bgm, duration, output_path, num_rounds, round_duration)
            except Exception as e:
                print(f"Aviso: No se pudo mezclar BGM externa ({e}). Generando pista sintética...")

        # 2. Respaldo: generar pista procedural completa
        self._synthesize_full_track(duration, output_path, num_rounds=num_rounds, round_duration=round_duration)
        return str(output_path)

    def _synthesize_sfx_track(self, duration, num_rounds, round_duration, output_path):
        """Genera únicamente los efectos de sonido (beeps de aviso y stingers de revelación)."""
        num_samples = int(self.sample_rate * duration)
        left = np.zeros(num_samples, dtype=np.float32)
        right = np.zeros(num_samples, dtype=np.float32)

        for r in range(num_rounds):
            round_start = r * round_duration
            reveal_time = round_start + 7.5
            round_end = min((r + 1) * round_duration, duration)

            # Beeps de Cuenta Atrás (a 5.5s y 6.5s de la ronda)
            beep_offsets = [5.5, 6.5]
            beep_freqs = [740.0, 987.77]  # F#5, B5
            for offset, freq in zip(beep_offsets, beep_freqs):
                b_time = round_start + offset
                b_idx = int(b_time * self.sample_rate)
                b_len = int(0.18 * self.sample_rate)
                if b_idx + b_len < num_samples:
                    t_b = np.linspace(0, 0.18, b_len, endpoint=False)
                    env = np.exp(-t_b * 18.0)
                    tone = np.sin(2 * np.pi * freq * t_b) * env * 0.45
                    left[b_idx:b_idx + b_len] += tone
                    right[b_idx:b_idx + b_len] += tone

            # Sonido de Revelación e Impacto en 7.5s de cada ronda
            rev_idx = int(reveal_time * self.sample_rate)
            boom_len = int(1.8 * self.sample_rate)
            if rev_idx + boom_len < num_samples:
                t_boom = np.linspace(0, 1.8, boom_len, endpoint=False)
                pitch_drop = 100.0 * np.exp(-t_boom * 3.5) + 45.0
                boom_wave = np.sin(2 * np.pi * pitch_drop * t_boom) * np.exp(-t_boom * 2.8) * 0.60
                left[rev_idx:rev_idx + boom_len] += boom_wave
                right[rev_idx:rev_idx + boom_len] += boom_wave

            # Acorde de Victoria (C Mayor para rondas 1 y 2, gran fanfarria para la ronda final)
            chord_dur = round_end - reveal_time
            chord_len = int(chord_dur * self.sample_rate)
            chord_end = min(rev_idx + chord_len, num_samples)
            actual_len = chord_end - rev_idx
            if actual_len > 0:
                t_chord = np.linspace(0, actual_len / self.sample_rate, actual_len, endpoint=False)
                decay_rate = 0.9 if r < num_rounds - 1 else 0.5
                env_chord = np.exp(-t_chord * decay_rate)
                chord = (
                    0.25 * np.sin(2 * np.pi * 523.25 * t_chord) +
                    0.25 * np.sin(2 * np.pi * 659.25 * t_chord) +
                    0.25 * np.sin(2 * np.pi * 783.99 * t_chord) +
                    0.25 * np.sin(2 * np.pi * 1046.50 * t_chord)
                ) * env_chord * 0.50
                left[rev_idx:chord_end] += chord
                right[rev_idx:chord_end] += chord

        # Normalizar
        max_val = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-5)
        if max_val > 0.95:
            left = (left / max_val) * 0.92
            right = (right / max_val) * 0.92

        left_int = (left * 32767).astype(np.int16)
        right_int = (right * 32767).astype(np.int16)

        interleaved = np.empty((num_samples * 2,), dtype=np.int16)
        interleaved[0::2] = left_int
        interleaved[1::2] = right_int

        with wave.open(str(output_path), 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(interleaved.tobytes())

        return str(output_path)

    def _mix_bgm_with_sfx(self, bgm_file, duration, output_path, num_rounds, round_duration):
        """Mezcla la pista de música de fondo con los efectos sonoros sintetizados."""
        sfx_temp = AUDIO_DIR / "_temp_sfx.wav"
        self._synthesize_sfx_track(duration, num_rounds, round_duration, sfx_temp)

        bgm_clip = AudioFileClip(str(bgm_file))

        # Ajustar duración de la música (repetir o recortar a 30s exactos)
        if bgm_clip.duration < duration:
            # Si la pista es más corta que 30s, hacer bucle
            repeats = int(np.ceil(duration / bgm_clip.duration))
            from moviepy import concatenate_audioclips
            bgm_clip = concatenate_audioclips([bgm_clip] * repeats)

        bgm_sub = bgm_clip.subclipped(0, duration).with_volume_scaled(0.38)
        sfx_clip = AudioFileClip(str(sfx_temp)).with_volume_scaled(0.95)

        composite = CompositeAudioClip([bgm_sub, sfx_clip])
        composite.write_audiofile(
            str(output_path),
            fps=self.sample_rate,
            logger=None
        )

        bgm_clip.close()
        bgm_sub.close()
        sfx_clip.close()
        composite.close()

        if sfx_temp.exists():
            try:
                sfx_temp.unlink()
            except Exception:
                pass

        return str(output_path)

    def _synthesize_full_track(self, duration, output_path, num_rounds=3, round_duration=10.0):
        """Generador procedural de respaldo de pista completa en caso de no haber BGM externa."""
        num_samples = int(self.sample_rate * duration)
        left = np.zeros(num_samples, dtype=np.float32)
        right = np.zeros(num_samples, dtype=np.float32)

        beat_interval = 60.0 / 130.0  # 130 BPM

        for r in range(num_rounds):
            round_start = r * round_duration
            reveal_time = round_start + 7.5
            round_end = min((r + 1) * round_duration, duration)

            tension_duration = reveal_time - round_start
            num_beats = int(tension_duration / beat_interval)

            for b in range(num_beats):
                beat_time = round_start + (b * beat_interval)
                sample_idx = int(beat_time * self.sample_rate)

                hit_len = int(0.24 * self.sample_rate)
                if sample_idx + hit_len < num_samples:
                    t_hit = np.linspace(0, 0.24, hit_len, endpoint=False)
                    freq = 65.41 if (b % 4 < 2) else 55.0
                    env = np.exp(-t_hit * 12.0)
                    hit_wave = np.sin(2 * np.pi * freq * t_hit) * env * 0.35

                    progress_in_round = (beat_time - round_start) / tension_duration
                    intensity = 0.5 + 0.5 * progress_in_round
                    left[sample_idx:sample_idx + hit_len] += hit_wave * intensity
                    right[sample_idx:sample_idx + hit_len] += hit_wave * intensity

                off_sample = sample_idx + int((beat_interval / 2) * self.sample_rate)
                tick_len = int(0.04 * self.sample_rate)
                if off_sample + tick_len < num_samples:
                    noise = (np.random.rand(tick_len) * 2.0 - 1.0) * np.exp(-np.linspace(0, 0.04, tick_len) * 80.0) * 0.08
                    left[off_sample:off_sample + tick_len] += noise
                    right[off_sample:off_sample + tick_len] += noise

            # Beeps
            beep_offsets = [5.5, 6.5]
            beep_freqs = [659.25, 880.0]
            for offset, freq in zip(beep_offsets, beep_freqs):
                b_time = round_start + offset
                b_idx = int(b_time * self.sample_rate)
                b_len = int(0.18 * self.sample_rate)
                if b_idx + b_len < num_samples:
                    t_b = np.linspace(0, 0.18, b_len, endpoint=False)
                    env = np.exp(-t_b * 16.0)
                    tone = np.sin(2 * np.pi * freq * t_b) * env * 0.38
                    left[b_idx:b_idx + b_len] += tone
                    right[b_idx:b_idx + b_len] += tone

            # Revelación e Impacto
            rev_idx = int(reveal_time * self.sample_rate)
            boom_len = int(2.0 * self.sample_rate)
            if rev_idx + boom_len < num_samples:
                t_boom = np.linspace(0, 2.0, boom_len, endpoint=False)
                pitch_drop = 95.0 * np.exp(-t_boom * 3.0) + 40.0
                boom_wave = np.sin(2 * np.pi * pitch_drop * t_boom) * np.exp(-t_boom * 2.5) * 0.55
                left[rev_idx:rev_idx + boom_len] += boom_wave
                right[rev_idx:rev_idx + boom_len] += boom_wave

            chord_dur = round_end - reveal_time
            chord_len = int(chord_dur * self.sample_rate)
            chord_end = min(rev_idx + chord_len, num_samples)
            actual_len = chord_end - rev_idx
            if actual_len > 0:
                t_chord = np.linspace(0, actual_len / self.sample_rate, actual_len, endpoint=False)
                decay_rate = 0.8 if r < num_rounds - 1 else 0.5
                env_chord = np.exp(-t_chord * decay_rate)
                chord = (
                    0.25 * np.sin(2 * np.pi * 523.25 * t_chord) +
                    0.25 * np.sin(2 * np.pi * 659.25 * t_chord) +
                    0.25 * np.sin(2 * np.pi * 783.99 * t_chord) +
                    0.25 * np.sin(2 * np.pi * 1046.50 * t_chord)
                ) * env_chord * 0.45
                left[rev_idx:chord_end] += chord
                right[rev_idx:chord_end] += chord

        max_val = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-5)
        if max_val > 0.95:
            left = (left / max_val) * 0.92
            right = (right / max_val) * 0.92

        left_int = (left * 32767).astype(np.int16)
        right_int = (right * 32767).astype(np.int16)

        interleaved = np.empty((num_samples * 2,), dtype=np.int16)
        interleaved[0::2] = left_int
        interleaved[1::2] = right_int

        with wave.open(str(output_path), 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(interleaved.tobytes())

        return str(output_path)
