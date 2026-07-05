import os
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import yt_dlp
from app.config import DOWNLOADS_DIR, AppConfig

class AudioService:
    @staticmethod
    async def download_from_youtube(url: str, format: str = "bestaudio") -> Optional[str]:
        output_path = DOWNLOADS_DIR / f"audio_{abs(hash(url))}"
        output_template = str(output_path / "%(title)s.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        try:
            os.makedirs(output_path, exist_ok=True)
            loop = asyncio.get_event_loop()

            def download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return info

            info = await loop.run_in_executor(None, download)

            files = list(output_path.glob("*.mp3")) + list(output_path.glob("*.m4a"))
            if files:
                return str(files[0])
            return None
        except Exception as e:
            raise Exception(f"Audio download failed: {e}")

    @staticmethod
    async def download_from_youtube_with_cookies(url: str, cookies_path: str) -> Optional[str]:
        output_path = DOWNLOADS_DIR / f"audio_{abs(hash(url))}"
        output_template = str(output_path / "%(title)s.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'cookiefile': cookies_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
        }

        try:
            os.makedirs(output_path, exist_ok=True)
            loop = asyncio.get_event_loop()

            def download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return info

            await loop.run_in_executor(None, download)
            files = list(output_path.glob("*.mp3")) + list(output_path.glob("*.m4a"))
            return str(files[0]) if files else None
        except Exception as e:
            raise Exception(f"Cookie-based download failed: {e}")

    @staticmethod
    async def get_audio_duration(audio_path: str) -> float:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())

    @staticmethod
    async def convert_to_wav(input_path: str, output_path: str = None) -> str:
        if output_path is None:
            output_path = str(Path(input_path).with_suffix('.wav'))

        cmd = ['ffmpeg', '-i', input_path, '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', '-y', output_path]
        subprocess.run(cmd, capture_output=True)
        return output_path
