import random
import asyncio
from pathlib import Path
from typing import Optional, List, Dict
import httpx
from app.config import DOWNLOADS_DIR, PexelsConfig

class BackgroundService:
    PEXELS_API = "https://api.pexels.com"

    @staticmethod
    async def search_pexels_video(query: str, per_page: int = 5) -> List[Dict]:
        headers = {"Authorization": PexelsConfig.api_key}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{BackgroundService.PEXELS_API}/videos/search",
                    params={"query": query, "per_page": per_page, "orientation": "landscape"},
                    headers=headers,
                    timeout=15
                )
                if resp.status_code == 200:
                    data = resp.json()
                    videos = []
                    for video in data.get("videos", []):
                        for file in video.get("video_files", []):
                            if file.get("quality") == "hd" and file.get("width", 0) >= 1920:
                                videos.append({
                                    "id": video["id"],
                                    "url": file["link"],
                                    "width": file.get("width"),
                                    "height": file.get("height"),
                                    "duration": video.get("duration"),
                                    "photographer": video.get("user", {}).get("name", ""),
                                })
                                break
                    return videos
            except:
                pass
        return []

    @staticmethod
    async def search_pexels_image(query: str, per_page: int = 5) -> List[Dict]:
        headers = {"Authorization": PexelsConfig.api_key}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{BackgroundService.PEXELS_API}/photos/search",
                    params={"query": query, "per_page": per_page, "orientation": "landscape"},
                    headers=headers,
                    timeout=15
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return [{
                        "id": photo["id"],
                        "url": photo["src"]["original"],
                        "width": photo.get("width"),
                        "height": photo.get("height"),
                        "photographer": photo.get("photographer", ""),
                    } for photo in data.get("photos", [])]
            except:
                pass
        return []

    @staticmethod
    async def download_background(url: str, track_name: str) -> Optional[str]:
        output_path = DOWNLOADS_DIR / f"bg_{track_name.replace(' ', '_')}"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, timeout=60, follow_redirects=True)
                if resp.status_code == 200:
                    ext = Path(url.split("?")[0]).suffix or ".mp4"
                    filepath = str(output_path.with_suffix(ext))
                    with open(filepath, "wb") as f:
                        f.write(resp.content)
                    return filepath
            except:
                pass
        return None

    @staticmethod
    async def generate_gradient_background(track_name: str, colors: List[str] = None) -> str:
        from PIL import Image, ImageDraw
        import numpy as np

        if colors is None:
            colors = [
                (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
            ]

        output_path = DOWNLOADS_DIR / f"gradient_{track_name.replace(' ', '_')}.png"
        width, height = 1920, 1080

        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)

        for y in range(height):
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * y / height)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * y / height)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * y / height)
            for x in range(width):
                draw.point((x, y), fill=(r, g, b))

        image.save(str(output_path))
        return str(output_path)

    @staticmethod
    async def create_particle_background(track_name: str) -> str:
        from PIL import Image, ImageDraw
        import random

        output_path = DOWNLOADS_DIR / f"particles_{track_name.replace(' ', '_')}.png"
        width, height = 1920, 1080

        image = Image.new('RGB', (width, height), (10, 10, 30))
        draw = ImageDraw.Draw(image)

        for _ in range(200):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 4)
            brightness = random.randint(50, 200)
            draw.ellipse(
                [x - size, y - size, x + size, y + size],
                fill=(brightness, brightness, brightness)
            )

        image.save(str(output_path))
        return str(output_path)
