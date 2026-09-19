import time
import schedule
from datetime import datetime, timedelta
from pathlib import Path

from .config import SCHEDULE_INTERVAL_HOURS
from .character_manager import CharacterManager
from .video_generator import VideoGenerator
from .uploaders.manager import UploadManager

class QuizScheduler:
    def __init__(self, interval_hours=SCHEDULE_INTERVAL_HOURS):
        self.interval_hours = interval_hours
        self.character_manager = CharacterManager()
        self.video_generator = VideoGenerator()
        self.upload_manager = UploadManager()

    def run_cycle(self, force_character_id=None):
        """Ejecuta un ciclo completo: selección, generación, publicación y registro."""
        print("\n" + "#"*55)
        print(f"⏰ [CICLO DE AUTOMATIZACIÓN] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("#"*55)

        # 1. Obtener siguiente personaje
        character = self.character_manager.get_next_character(force_id=force_character_id)
        print(f"🎯 Personaje seleccionado: {character['name']} ({character.get('game', '')})")

        # 2. Generar video en Blurred_characters/
        video_path, metadata = self.video_generator.generate_video(character)

        # 3. Intentar publicación en redes
        updated_metadata = self.upload_manager.process_uploads(video_path, metadata)

        # 4. Registrar en historial para no repetir
        self.character_manager.record_usage(character["id"], video_path, updated_metadata)

        next_time = datetime.now() + timedelta(hours=self.interval_hours)
        print(f"🎉 Ciclo completado para '{character['name']}'.")
        print(f"🕒 Próxima generación programada para: {next_time.strftime('%Y-%m-%d %H:%M:%S')} (dentro de {self.interval_hours}h)")
        print("#"*55 + "\n")

        return video_path, updated_metadata

    def start(self, run_immediately=True):
        """Inicia el bucle continuo cada N horas."""
        print("\n" + "="*55)
        print(f"🚀 Iniciando Programador Automático de Videos")
        print(f"⏱️ Frecuencia: Cada {self.interval_hours} horas")
        print(f"📁 Destino: Carpeta Blurred_characters/")
        print("Presiona Ctrl + C en cualquier momento para detener.")
        print("="*55 + "\n")

        if run_immediately:
            print("▶️ Ejecutando el primer video del ciclo de inmediato...")
            try:
                self.run_cycle()
            except Exception as e:
                print(f"❌ Error en el ciclo inicial: {e}")

        # Programar cada N horas
        schedule.every(self.interval_hours).hours.do(self.run_cycle)

        try:
            while True:
                schedule.run_pending()
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n🛑 Programador detenido por el usuario.")
