import wave
import numpy as np
from pathlib import Path
from .config import AUDIO_DIR, VIDEO_DURATION

class AudioEngine:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def get_or_create_soundtrack(self, duration=VIDEO_DURATION, output_path=None):
        """
        Genera una pista de audio completa con música de suspense progresiva,
        sonidos de cuenta atrás (3, 2, 1) y efecto de revelación triunfal.
        Si el usuario coloca archivos personalizados en assets/audio, los usará.
        """
        if output_path is None:
            output_path = AUDIO_DIR / "soundtrack.wav"

        # Si ya existe un soundtrack prefabricado o generado recientemente de la misma duración
        custom_bgm = AUDIO_DIR / "custom_bgm.mp3"
        if custom_bgm.exists():
            return str(custom_bgm)

        self._synthesize_full_track(duration, output_path)
        return str(output_path)

    def _synthesize_full_track(self, duration, output_path):
        num_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, num_samples, endpoint=False)

        # Canal Izquierdo y Derecho (Stereo)
        left = np.zeros(num_samples, dtype=np.float32)
        right = np.zeros(num_samples, dtype=np.float32)

        # 1. Base rítmica de tensión (0 a 9s)
        # Tempo: 130 BPM -> 1 beat = 60 / 130 = 0.4615 segundos
        beat_interval = 60.0 / 130.0
        num_beats = int(9.0 / beat_interval)

        for b in range(num_beats):
            beat_time = b * beat_interval
            sample_idx = int(beat_time * self.sample_rate)

            # Golpe de bajo sintetizado (pulso de 0.25s)
            hit_len = int(0.25 * self.sample_rate)
            if sample_idx + hit_len < num_samples:
                t_hit = np.linspace(0, 0.25, hit_len, endpoint=False)
                # Frecuencia base baja con ligera modulación
                freq = 65.41 if (b % 4 < 2) else 55.0  # C2 / A1
                env = np.exp(-t_hit * 12.0)  # Decaimiento rápido
                hit_wave = np.sin(2 * np.pi * freq * t_hit) * env * 0.35

                # Subir volumen gradualmente conforme avanza el misterio
                intensity = 0.5 + 0.5 * (beat_time / 9.0)
                left[sample_idx:sample_idx + hit_len] += hit_wave * intensity
                right[sample_idx:sample_idx + hit_len] += hit_wave * intensity

            # Pulso secundario (hi-hat / tick sutil) en contratiempos
            off_sample = sample_idx + int((beat_interval / 2) * self.sample_rate)
            tick_len = int(0.04 * self.sample_rate)
            if off_sample + tick_len < num_samples:
                noise = (np.random.rand(tick_len) * 2.0 - 1.0) * np.exp(-np.linspace(0, 0.04, tick_len) * 80.0) * 0.08
                left[off_sample:off_sample + tick_len] += noise
                right[off_sample:off_sample + tick_len] += noise

        # 2. Beeps de Cuenta Atrás a los segundos 6.5, 7.5 y 8.5
        beep_times = [6.5, 7.5, 8.5]
        beep_freqs = [659.25, 783.99, 1046.50]  # E5, G5, C6 (tono ascendente)
        for b_time, freq in zip(beep_times, beep_freqs):
            b_idx = int(b_time * self.sample_rate)
            b_len = int(0.18 * self.sample_rate)
            if b_idx + b_len < num_samples:
                t_b = np.linspace(0, 0.18, b_len, endpoint=False)
                env = np.exp(-t_b * 16.0)
                tone = np.sin(2 * np.pi * freq * t_b) * env * 0.4
                left[b_idx:b_idx + b_len] += tone
                right[b_idx:b_idx + b_len] += tone

        # 3. Sonido de REVELACIÓN e IMPACTO en el segundo 9.0
        rev_idx = int(9.0 * self.sample_rate)
        # Impacto de bajo (Boom cinematográfico)
        boom_len = int(2.0 * self.sample_rate)
        if rev_idx + boom_len < num_samples:
            t_boom = np.linspace(0, 2.0, boom_len, endpoint=False)
            pitch_drop = 90.0 * np.exp(-t_boom * 3.0) + 40.0
            boom_wave = np.sin(2 * np.pi * pitch_drop * t_boom) * np.exp(-t_boom * 2.5) * 0.55
            left[rev_idx:rev_idx + boom_len] += boom_wave
            right[rev_idx:rev_idx + boom_len] += boom_wave

        # Acorde de Victoria / Fanfarria (C Mayor: C5, E5, G5, C6)
        chord_len = int(3.5 * self.sample_rate)
        chord_end = min(rev_idx + chord_len, num_samples)
        actual_len = chord_end - rev_idx
        if actual_len > 0:
            t_chord = np.linspace(0, actual_len / self.sample_rate, actual_len, endpoint=False)
            env_chord = np.exp(-t_chord * 0.9)
            chord = (
                0.25 * np.sin(2 * np.pi * 523.25 * t_chord) +
                0.25 * np.sin(2 * np.pi * 659.25 * t_chord) +
                0.25 * np.sin(2 * np.pi * 783.99 * t_chord) +
                0.25 * np.sin(2 * np.pi * 1046.50 * t_chord)
            ) * env_chord * 0.45
            left[rev_idx:chord_end] += chord
            right[rev_idx:chord_end] += chord

        # Normalizar para evitar clipping
        max_val = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-5)
        if max_val > 0.95:
            left = (left / max_val) * 0.92
            right = (right / max_val) * 0.92

        # Convertir a 16-bit PCM estéreo
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
