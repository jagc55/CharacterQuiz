import json
from pathlib import Path
from .youtube_uploader import YouTubeUploader
from .tiktok_uploader import TikTokUploader

class UploadManager:
    def __init__(self):
        self.youtube = YouTubeUploader()
        self.tiktok = TikTokUploader()

    def process_uploads(self, video_path, metadata):
        """
        Intenta publicar el video en YouTube Shorts y TikTok.
        Actualiza el archivo .json de metadatos con las respuestas y enlaces.
        """
        video_path = Path(video_path)
        meta_file = video_path.with_suffix(".json")

        print("\n" + "-"*40)
        print("🚀 Procesando subida a plataformas sociales...")
        print("-"*40)

        # 1. YouTube Shorts
        yt_res = self.youtube.upload_short(video_path, metadata)
        metadata["youtube_status"] = yt_res.get("status")
        if "url" in yt_res:
            metadata["youtube_url"] = yt_res["url"]

        # 2. TikTok
        tt_res = self.tiktok.upload_video(video_path, metadata)
        metadata["tiktok_status"] = tt_res.get("status")
        if "publish_id" in tt_res:
            metadata["tiktok_publish_id"] = tt_res["publish_id"]

        # Actualizar archivo de metadatos en Blurred_characters/
        if meta_file.exists():
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

        print("-" * 40 + "\n")
        return metadata
