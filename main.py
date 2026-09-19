import sys
import argparse
from pathlib import Path

# Configurar UTF-8 en Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from src.config import SCHEDULE_INTERVAL_HOURS, OUTPUT_DIR
from src.character_manager import CharacterManager
from src.scheduler import QuizScheduler

def print_banner():
    print("""
=============================================================
  🎮 GENERADOR AUTOMÁTICO DE SHORTS & TIKTOK 🎮
        "ADIVINA EL PERSONAJE DE VIDEOJUEGOS"
=============================================================
    """)

def list_characters():
    cm = CharacterManager()
    used_ids = set(cm.get_used_character_ids())
    print("\n--- Catálogo de Personajes ---")
    for i, char in enumerate(cm.characters, 1):
        status = "✅ Usado" if char["id"] in used_ids else "⏳ Pendiente"
        print(f"{i:2d}. [{status}] {char['name']} - {char.get('game', '')} (ID: {char['id']})")
    print(f"\nTotal: {len(cm.characters)} personajes | Usados: {len(used_ids)} | Disponibles: {len(cm.characters) - len(used_ids)}\n")

def main():
    print_banner()

    parser = argparse.ArgumentParser(description="Generador automático de videos de personajes difuminados para TikTok y Shorts")
    parser.add_argument("--once", action="store_true", help="Genera un único video ahora mismo y finaliza.")
    parser.add_argument("--schedule", action="store_true", help="Inicia la automatización continua cada 4 horas.")
    parser.add_argument("--interval", type=int, default=SCHEDULE_INTERVAL_HOURS, help=f"Intervalo de horas entre videos (por defecto {SCHEDULE_INTERVAL_HOURS}h).")
    parser.add_argument("--character", type=str, help="Fuerza la generación de un personaje concreto por su ID.")
    parser.add_argument("--list-characters", action="store_true", help="Muestra la lista de personajes disponibles y su estado en el historial.")

    args = parser.parse_args()

    if args.list_characters:
        list_characters()
        return

    scheduler = QuizScheduler(interval_hours=args.interval)

    if args.once:
        print("🎯 Modo generación única seleccionado.")
        scheduler.run_cycle(force_character_id=args.character)
        print(f"📁 Revisa tu carpeta: {OUTPUT_DIR.resolve()}\n")
        return

    if args.schedule:
        scheduler.start(run_immediately=True)
        return

    # Si se ejecuta sin argumentos, mostramos ayuda y opciones rápidas
    print("Opciones de ejecución:")
    print("  python main.py --once                   -> Genera 1 video de prueba ahora mismo.")
    print("  python main.py --schedule               -> Inicia el ciclo automático cada 4 horas.")
    print("  python main.py --list-characters        -> Ver lista de personajes y estado.")
    print("  python main.py --character <id> --once  -> Genera video de un personaje específico.\n")

if __name__ == "__main__":
    main()
