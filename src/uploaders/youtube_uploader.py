import os
import json
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

class YouTubeUploader:
    def __init__(self, client_secrets_file=None, token_file=None):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.client_secrets_file = client_secrets_file or (base_dir / "client_secret.json")
        self.token_file = token_file or (base_dir / "youtube_token.json")

    def is_configured(self):
        """Comprueba si el archivo de secretos de cliente de Google Cloud existe."""
        return Path(self.client_secrets_file).exists() or Path(self.token_file).exists()

    def get_authenticated_service(self):
        creds = None
        if Path(self.token_file).exists():
            creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not Path(self.client_secrets_file).exists():
                    raise FileNotFoundError(
                        f"No se encontró el archivo '{self.client_secrets_file}'. "
                        "Descárgalo desde Google Cloud Console para habilitar la subida automática a YouTube Shorts."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(str(self.client_secrets_file), SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.token_file, "w") as token:
                token.write(creds.to_json())

        return build("youtube", "v3", credentials=creds)

    def upload_short(self, video_path, metadata):
        """
        Sube el video como YouTube Short.
        Los videos verticales (<60s) con #Shorts en título/descripción son indexados automáticamente como Shorts.
        """
        if not self.is_configured():
            print("\n[YouTube Shorts] ℹ️ API no configurada aún (falta client_secret.json).")
            print("El video ha quedado guardado listo en Blurred_characters/")
            return {"status": "SKIPPED_NO_CREDENTIALS", "video_id": None}

        try:
            youtube = self.get_authenticated_service()

            title = metadata.get("title", "¿Quién es este personaje? #Shorts")
            description = metadata.get("description", "")
            tags = metadata.get("tags", ["Shorts", "Gaming", "AdivinaElPersonaje"])

            body = {
                "snippet": {
                    "title": title[:100],
                    "description": description,
                    "tags": [t.replace("#", "") for t in tags],
                    "categoryId": "20"  # Categoría Gaming / Videojuegos
                },
                "status": {
                    "privacyStatus": os.getenv("YOUTUBE_PRIVACY_STATUS", "public"),
                    "selfDeclaredMadeForKids": False
                }
            }

            media = MediaFileUpload(
                str(video_path),
                mimetype="video/mp4",
                resumable=True,
                chunksize=1024*1024*4
            )

            print(f"[YouTube Shorts] Subiendo {video_path.name}...")
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Subiendo a YouTube: {int(status.progress() * 100)}%")

            video_id = response.get("id")
            video_url = f"https://youtube.com/shorts/{video_id}"
            print(f"[YouTube Shorts] ✅ ¡Video publicado con éxito! URL: {video_url}")

            return {
                "status": "SUCCESS",
                "video_id": video_id,
                "url": video_url
            }

        except Exception as e:
            print(f"[YouTube Shorts] ❌ Error durante la subida: {e}")
            return {"status": "ERROR", "error": str(e)}
