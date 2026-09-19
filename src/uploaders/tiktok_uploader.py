import os
import requests
from pathlib import Path
from ..config import TIKTOK_ACCESS_TOKEN

class TikTokUploader:
    def __init__(self, access_token=None):
        self.access_token = access_token or TIKTOK_ACCESS_TOKEN

    def is_configured(self):
        return bool(self.access_token and len(self.access_token.strip()) > 10)

    def upload_video(self, video_path, metadata):
        """
        Sube el video mediante la API oficial de TikTok (Content Posting API v2)
        o registra el estado si aún no está configurado.
        """
        if not self.is_configured():
            print("[TikTok] ℹ️ Token de TikTok no configurado en .env (TIKTOK_ACCESS_TOKEN).")
            print("El video ha quedado guardado listo en Blurred_characters/")
            return {"status": "SKIPPED_NO_CREDENTIALS", "post_id": None}

        try:
            print(f"[TikTok] Iniciando publicación de {Path(video_path).name}...")
            video_file = Path(video_path)
            file_size = video_file.stat().st_size

            # 1. Inicializar la publicación (Direct Post API de TikTok)
            init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json; charset=UTF-8"
            }

            title = metadata.get("title", "¿Quién es este personaje? #Gaming")
            payload = {
                "post_info": {
                    "title": title[:150],
                    "privacy_level": os.getenv("TIKTOK_PRIVACY_LEVEL", "PUBLIC_TO_EVERYONE"),
                    "disable_duet": False,
                    "disable_stitch": False,
                    "disable_comment": False
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": file_size,
                    "chunk_size": file_size,
                    "total_chunk_count": 1
                }
            }

            init_resp = requests.post(init_url, headers=headers, json=payload, timeout=20)
            if init_resp.status_code != 200:
                print(f"[TikTok] ❌ Error inicializando subida: {init_resp.text}")
                return {"status": "ERROR", "details": init_resp.text}

            data = init_resp.json().get("data", {})
            upload_url = data.get("upload_url")
            publish_id = data.get("publish_id")

            if not upload_url:
                return {"status": "ERROR", "details": "No se recibió upload_url de TikTok"}

            # 2. Transferir el archivo de video binario al servidor de TikTok
            with open(video_file, "rb") as f:
                upload_headers = {
                    "Content-Type": "video/mp4",
                    "Content-Range": f"bytes 0-{file_size - 1}/{file_size}"
                }
                put_resp = requests.put(upload_url, headers=upload_headers, data=f, timeout=60)

            if put_resp.status_code in [200, 201, 206]:
                print(f"[TikTok] ✅ ¡Video subido con éxito! Publish ID: {publish_id}")
                return {
                    "status": "SUCCESS",
                    "publish_id": publish_id
                }
            else:
                print(f"[TikTok] ❌ Error enviando archivo: {put_resp.status_code}")
                return {"status": "ERROR", "details": put_resp.text}

        except Exception as e:
            print(f"[TikTok] ❌ Excepción durante la subida: {e}")
            return {"status": "ERROR", "error": str(e)}
