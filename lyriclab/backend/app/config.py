import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("LYRICLAB_DATA_DIR", "/data"))
DOWNLOADS_DIR = Path(os.getenv("LYRICLAB_DOWNLOADS_DIR", "/downloads"))
OUTPUT_DIR = Path(os.getenv("LYRICLAB_OUTPUT_DIR", "/output"))

for d in [DATA_DIR, DOWNLOADS_DIR, OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)

try:
    from app.secrets import (
        FIREBASE_API_KEY, FIREBASE_AUTH_DOMAIN, FIREBASE_PROJECT_ID,
        FIREBASE_STORAGE_BUCKET, FIREBASE_MESSAGING_SENDER_ID,
        FIREBASE_APP_ID, FIREBASE_MEASUREMENT_ID,
        YOUTUBE_API_KEY, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET,
        YOUTUBE_PROJECT_ID, PEXELS_API_KEY,
    )
except ImportError:
    FIREBASE_API_KEY = os.getenv("NEXT_PUBLIC_FIREBASE_API_KEY")
    FIREBASE_AUTH_DOMAIN = os.getenv("NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN")
    FIREBASE_PROJECT_ID = os.getenv("NEXT_PUBLIC_FIREBASE_PROJECT_ID")
    FIREBASE_STORAGE_BUCKET = os.getenv("NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET")
    FIREBASE_MESSAGING_SENDER_ID = os.getenv("NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID")
    FIREBASE_APP_ID = os.getenv("NEXT_PUBLIC_FIREBASE_APP_ID")
    FIREBASE_MEASUREMENT_ID = os.getenv("NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
    YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
    YOUTUBE_PROJECT_ID = os.getenv("YOUTUBE_PROJECT_ID")
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

class FirebaseConfig:
    api_key = FIREBASE_API_KEY
    auth_domain = FIREBASE_AUTH_DOMAIN
    project_id = FIREBASE_PROJECT_ID
    storage_bucket = FIREBASE_STORAGE_BUCKET
    messaging_sender_id = FIREBASE_MESSAGING_SENDER_ID
    app_id = FIREBASE_APP_ID
    measurement_id = FIREBASE_MEASUREMENT_ID

class YouTubeConfig:
    api_key = YOUTUBE_API_KEY
    client_id = YOUTUBE_CLIENT_ID
    client_secret = YOUTUBE_CLIENT_SECRET
    project_id = YOUTUBE_PROJECT_ID
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://oauth2.googleapis.com/token"

class PexelsConfig:
    api_key = PEXELS_API_KEY

class AppConfig:
    debug = os.getenv("LYRICLAB_DEBUG", "true").lower() == "true"
    max_file_size = 500 * 1024 * 1024
    allowed_audio_formats = [".mp3", ".wav", ".m4a", ".flac", ".ogg"]
    allowed_video_formats = [".mp4", ".webm", ".mkv"]
    max_concurrent_jobs = int(os.getenv("LYRICLAB_MAX_JOBS", "4"))
    default_fps = 60
    default_resolution = "1920x1080"
    default_bitrate = "10M"
    preview_fps = 15
    preview_resolution = "854x480"
    preview_bitrate = "1M"
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
