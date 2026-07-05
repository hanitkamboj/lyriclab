import asyncio
import json
from typing import Optional, Dict, List, Tuple
from pathlib import Path
from app.services.audio_service import AudioService
from app.services.lyrics_service import LyricsService
from app.services.background_service import BackgroundService
from app.services.render_service import RenderService

class LyricsAgent:
    @staticmethod
    async def process_song(
        title: str,
        artist: str = "",
        song_url: str = "",
        audio_path: str = "",
        lyrics_path: str = "",
        background_path: str = "",
        style: str = "7clouds",
        resolution: str = "1920x1080",
        fps: int = 60,
        bitrate: str = "10M",
    ) -> Dict:
        result = {
            "title": title,
            "artist": artist,
            "status": "processing",
            "steps": {},
        }

        # Step 1: Get audio
        if not audio_path and song_url:
            try:
                audio_path = await AudioService.download_from_youtube(song_url)
                result["steps"]["audio"] = {"status": "done", "path": audio_path}
            except Exception as e:
                result["steps"]["audio"] = {"status": "failed", "error": str(e)}
                result["status"] = "failed"
                return result
        elif audio_path:
            result["steps"]["audio"] = {"status": "provided", "path": audio_path}
        else:
            result["steps"]["audio"] = {"status": "failed", "error": "No audio source"}
            result["status"] = "failed"
            return result

        # Step 2: Get lyrics
        if not lyrics_path:
            try:
                lrc_content = await LyricsService.get_lrc_from_lrclib(title, artist)
                if lrc_content:
                    lyrics_path = str(Path(audio_path).parent / f"{title}.lrc")
                    with open(lyrics_path, "w") as f:
                        f.write(lrc_content)
                    result["steps"]["lyrics"] = {"status": "done", "source": "lrclib"}
                else:
                    plain_lyrics = await LyricsService.fetch_from_azlyrics(title, artist)
                    if plain_lyrics:
                        audio_duration = await AudioService.get_audio_duration(audio_path)
                        lrc_content = await LyricsService.create_lrc_from_plain(plain_lyrics, audio_duration)
                        lyrics_path = str(Path(audio_path).parent / f"{title}.lrc")
                        with open(lyrics_path, "w") as f:
                            f.write(lrc_content)
                        result["steps"]["lyrics"] = {"status": "done", "source": "azlyrics"}
                    else:
                        result["steps"]["lyrics"] = {"status": "failed", "error": "No lyrics found"}
            except Exception as e:
                result["steps"]["lyrics"] = {"status": "failed", "error": str(e)}
        else:
            result["steps"]["lyrics"] = {"status": "provided"}

        # Step 3: Get background
        if not background_path:
            try:
                search_query = f"{title} {artist} music"
                videos = await BackgroundService.search_pexels_video(search_query)
                if videos:
                    bg_path = await BackgroundService.download_background(videos[0]["url"], title)
                    if bg_path:
                        background_path = bg_path
                        result["steps"]["background"] = {"status": "done", "source": "pexels_video"}
                    else:
                        images = await BackgroundService.search_pexels_image(search_query)
                        if images:
                            bg_path = await BackgroundService.download_background(images[0]["url"], title)
                            if bg_path:
                                background_path = bg_path
                                result["steps"]["background"] = {"status": "done", "source": "pexels_image"}
                if not background_path:
                    background_path = await BackgroundService.create_particle_background(title)
                    result["steps"]["background"] = {"status": "done", "source": "generated"}
            except Exception as e:
                background_path = await BackgroundService.generate_gradient_background(title)
                result["steps"]["background"] = {"status": "done", "source": "gradient_fallback"}
        else:
            result["steps"]["background"] = {"status": "provided"}

        result["audio_path"] = audio_path
        result["lyrics_path"] = lyrics_path
        result["background_path"] = background_path
        result["status"] = "ready"

        return result

    @staticmethod
    async def render_preview(result: Dict) -> Dict:
        preview_path = str(OUTPUT_DIR / f"preview_{Path(result['audio_path']).stem}.mp4")
        try:
            output = await RenderService.render_preview(
                audio_path=result["audio_path"],
                lyrics_path=result["lyrics_path"],
                background_path=result["background_path"],
                output_path=preview_path,
                style=result.get("style", "7clouds"),
            )
            result["preview_path"] = output
            result["status"] = "preview_ready"
        except Exception as e:
            result["status"] = "preview_failed"
            result["error"] = str(e)

        return result

    @staticmethod
    async def render_full(result: Dict) -> Dict:
        output_path = str(OUTPUT_DIR / f"final_{Path(result['audio_path']).stem}.mp4")
        try:
            output = await RenderService.render_full(
                audio_path=result["audio_path"],
                lyrics_path=result["lyrics_path"],
                background_path=result["background_path"],
                output_path=output_path,
                style=result.get("style", "7clouds"),
                resolution=result.get("resolution", "1920x1080"),
                fps=result.get("fps", 60),
                bitrate=result.get("bitrate", "10M"),
            )
            result["output_path"] = output
            result["status"] = "rendered"

            thumbnail_path = str(OUTPUT_DIR / f"thumb_{Path(result['audio_path']).stem}.jpg")
            await RenderService.create_thumbnail(
                audio_path=result["audio_path"],
                title=result["title"],
                artist=result.get("artist", ""),
                output_path=thumbnail_path,
            )
            result["thumbnail_path"] = thumbnail_path
        except Exception as e:
            result["status"] = "render_failed"
            result["error"] = str(e)

        return result

from app.config import OUTPUT_DIR
