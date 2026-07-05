"""
Secrets configuration.
Copy to secrets.py and fill in your API keys,
or set the corresponding environment variables.
"""

import os

def _e(key: str, default: str = "") -> str:
    return os.environ.get(key, default)

# --- Firebase (from sonifall project) ---
FIREBASE_API_KEY = _e("NEXT_PUBLIC_FIREBASE_API_KEY")
FIREBASE_AUTH_DOMAIN = _e("NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN")
FIREBASE_PROJECT_ID = _e("NEXT_PUBLIC_FIREBASE_PROJECT_ID")
FIREBASE_STORAGE_BUCKET = _e("NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET")
FIREBASE_MESSAGING_SENDER_ID = _e("NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID")
FIREBASE_APP_ID = _e("NEXT_PUBLIC_FIREBASE_APP_ID")
FIREBASE_MEASUREMENT_ID = _e("NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID")

# --- YouTube Data API v3 ---
YOUTUBE_API_KEY = _e("YOUTUBE_API_KEY")
YOUTUBE_CLIENT_ID = _e("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = _e("YOUTUBE_CLIENT_SECRET")
YOUTUBE_PROJECT_ID = _e("YOUTUBE_PROJECT_ID")

# --- Pexels (for backgrounds) ---
PEXELS_API_KEY = _e("PEXELS_API_KEY")
