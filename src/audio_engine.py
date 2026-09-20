import os
import sys
import random
import wave
import numpy as np
from pathlib import Path

# Configurar salida UTF-8 en Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from moviepy import AudioFileClip, CompositeAudioClip
from .config import (
    AUDIO_DIR,
    BGM_DIR,
    VIDEO_DURATION,
    CHARACTERS_PER_VIDEO,
    ROUND_DURATION,
    ROUND_REVEAL_START
)

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
                print(f"[Audio] Música de fondo seleccionada (sin copyright): {selected_bgm.name}")
                return self._mix_bgm_with_sfx(selected_bgm, duration, output_path, num_rounds, round_duration)
            except Exception as e:
                print(f"Aviso: No se pudo mezclar BGM externa ({e}). Generando pista sintética...")

        # 2. Respaldo: generar pista procedural completa
        self._synthesize_full_track(duration, output_path, num_rounds=num_rounds, round_duration=round_duration)
        return str(output_path)

    def _generate_clock_tick(self, is_tock=False):
        """Genera un tic/tac mecánico y nítido de cronómetro/reloj analógico."""
        dur = 0.035
        n = int(self.sample_rate * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        f1 = 1950.0 if not is_tock else 1450.0
        f2 = 3300.0 if not is_tock else 2700.0
        click1 = (np.sin(2 * np.pi * f1 * t) * 0.65 + np.sin(2 * np.pi * f2 * t) * 0.35) * np.exp(-t * 180.0)
        delay_samples = int(0.003 * self.sample_rate)
        click2 = np.zeros(n)
        t_del = t[:-delay_samples]
        click2[delay_samples:] = (np.sin(2 * np.pi * (f1 * 1.1) * t_del) * 0.4) * np.exp(-t_del * 220.0)
        noise = np.random.normal(0, 0.08, n) * np.exp(-t * 260.0)
        out = (click1 + click2 + noise)
        return (out / max(np.max(np.abs(out)), 1e-5) * 0.32).astype(np.float32)

    def _generate_analog_alarm_bell(self, duration=1.4):
        """Genera el repiqueteo metálico característico de un despertador analógico de doble campana."""
        num_samples = int(self.sample_rate * duration)
        out = np.zeros(num_samples, dtype=np.float32)
        strike_freq = 22.0
        num_strikes = int(duration * strike_freq)
        f0_bell1 = 2180.0
        modes1 = [f0_bell1 * 1.0, f0_bell1 * 1.58, f0_bell1 * 2.15, f0_bell1 * 2.75]
        f0_bell2 = 2520.0
        modes2 = [f0_bell2 * 1.0, f0_bell2 * 1.58, f0_bell2 * 2.15, f0_bell2 * 2.75]
        strike_dur = 0.075
        strike_samples = int(strike_dur * self.sample_rate)
        t_s = np.linspace(0, strike_dur, strike_samples, endpoint=False)
        for s in range(num_strikes):
            t_start = s / strike_freq
            idx_start = int(t_start * self.sample_rate)
            if idx_start + strike_samples >= num_samples:
                break
            modes = modes1 if s % 2 == 0 else modes2
            bell_hit = (
                0.50 * np.sin(2 * np.pi * modes[0] * t_s) * np.exp(-t_s * 40.0) +
                0.28 * np.sin(2 * np.pi * modes[1] * t_s) * np.exp(-t_s * 60.0) +
                0.15 * np.sin(2 * np.pi * modes[2] * t_s) * np.exp(-t_s * 85.0) +
                0.07 * np.sin(2 * np.pi * modes[3] * t_s) * np.exp(-t_s * 110.0)
            )
            clatter = np.random.uniform(-1, 1, strike_samples) * np.exp(-t_s * 350.0) * 0.2
            env = 1.0 if s < num_strikes - 4 else (num_strikes - s) / 4.0
            out[idx_start:idx_start + strike_samples] += (bell_hit + clatter) * env
        return (out / max(np.max(np.abs(out)), 1e-5) * 0.60).astype(np.float32)

    def _get_traditional_alarm_sound(self):
        """Obtiene el sonido real de un despertador analógico metálico tradicional (doble campana)."""
        alarm_wav_path = AUDIO_DIR / "sfx" / "alarm_clock_ring.wav"
        if alarm_wav_path.exists():
            try:
                with wave.open(str(alarm_wav_path), 'rb') as wf:
                    w_nch = wf.getnchannels()
                    w_frames = wf.readframes(wf.getnframes())
                    raw_sig = np.frombuffer(w_frames, dtype=np.int16).astype(np.float32) / 32767.0
                    if w_nch == 2:
                        raw_sig = raw_sig.reshape(-1, 2)
                        return raw_sig[:, 0], raw_sig[:, 1]
                    else:
                        return raw_sig, raw_sig
            except Exception as e:
                print(f"Aviso: Error cargando {alarm_wav_path} ({e}), usando respaldo sintetizado.")

        synth = self._generate_analog_alarm_bell(duration=1.6)
        return synth, synth

    def _synthesize_sfx_track(self, duration, num_rounds, round_duration, output_path):
        """Genera los efectos de sonido: reloj/cronómetro durante el temporizador y despertador analógico tradicional al finalizar."""
        num_samples = int(self.sample_rate * duration)
        left = np.zeros(num_samples, dtype=np.float32)
        right = np.zeros(num_samples, dtype=np.float32)

        tick = self._generate_clock_tick(is_tock=False)
        tock = self._generate_clock_tick(is_tock=True)
        alarm_left, alarm_right = self._get_traditional_alarm_sound()

        for r in range(num_rounds):
            round_start = r * round_duration
            reveal_time = round_start + ROUND_REVEAL_START

            # 1. Reloj / Cronómetro mientras baja la barra del temporizador (cada 0.5s hasta reveal_time)
            num_ticks = int(ROUND_REVEAL_START / 0.5)
            for i in range(1, num_ticks):
                t_tick = round_start + (i * 0.5)
                if t_tick >= reveal_time:
                    break
                t_idx = int(t_tick * self.sample_rate)
                snd = tock if (i % 2 == 0) else tick
                snd_len = len(snd)
                if t_idx + snd_len < num_samples:
                    left[t_idx:t_idx + snd_len] += snd
                    right[t_idx:t_idx + snd_len] += snd

            # 2. Despertador analógico metálico tradicional al llegar al final del tiempo (12s)
            rev_idx = int(reveal_time * self.sample_rate)
            bell_len = min(len(alarm_left), num_samples - rev_idx)
            if rev_idx < num_samples and bell_len > 0:
                left[rev_idx:rev_idx + bell_len] += alarm_left[:bell_len] * 0.75
                right[rev_idx:rev_idx + bell_len] += alarm_right[:bell_len] * 0.75

        # En la pantalla final (Outro) NO se reproduce ningún sonido de fin ni alarma
        # Normalizar si es necesario
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

        bgm_sub = bgm_clip.subclipped(0, duration).with_volume_scaled(0.60)
        sfx_clip = AudioFileClip(str(sfx_temp)).with_volume_scaled(0.40)

        composite = CompositeAudioClip([bgm_sub, sfx_clip])
        out_p = Path(output_path)
        out_p.unlink(missing_ok=True)
        composite.write_audiofile(
            str(out_p),
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

        alarm_left, alarm_right = self._get_traditional_alarm_sound()
        tick = self._generate_clock_tick(is_tock=False)
        tock = self._generate_clock_tick(is_tock=True)

        for r in range(num_rounds):
            round_start = r * round_duration
            reveal_time = round_start + ROUND_REVEAL_START
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

            # Reloj / Cronómetro mientras baja la barra (cada 0.5s)
            num_ticks = int(ROUND_REVEAL_START / 0.5)
            for i in range(1, num_ticks):
                t_tick = round_start + (i * 0.5)
                if t_tick >= reveal_time:
                    break
                t_idx = int(t_tick * self.sample_rate)
                snd = tock if (i % 2 == 0) else tick
                snd_len = len(snd)
                if t_idx + snd_len < num_samples:
                    left[t_idx:t_idx + snd_len] += snd
                    right[t_idx:t_idx + snd_len] += snd

            # Despertador analógico metálico tradicional al llegar a los 15s
            rev_idx = int(reveal_time * self.sample_rate)
            bell_len = min(len(alarm_left), num_samples - rev_idx)
            if rev_idx < num_samples and bell_len > 0:
                left[rev_idx:rev_idx + bell_len] += alarm_left[:bell_len] * 0.75
                right[rev_idx:rev_idx + bell_len] += alarm_right[:bell_len] * 0.75

        max_val = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-5)
        if max_val > 0.95:
            left = (left / max_val) * 0.92
            right = (right / max_val) * 0.92

        left_int = (left * 32767).astype(np.int16)
        right_int = (right * 32767).astype(np.int16)

        interleaved = np.empty((num_samples * 2,), dtype=np.int16)
        interleaved[0::2] = left_int
        interleaved[1::2] = right_int

        Path(output_path).unlink(missing_ok=True)
        with wave.open(str(output_path), 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(interleaved.tobytes())

        return str(output_path)
