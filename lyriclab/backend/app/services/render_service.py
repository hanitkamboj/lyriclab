import subprocess
import json
import asyncio
import os
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from app.config import OUTPUT_DIR, AppConfig
from app.services.lyrics_service import LyricsService

class RenderService:
    @staticmethod
    async def render_preview(
        audio_path: str,
        lyrics_path: str,
        background_path: str,
        output_path: str,
        style: str = "7clouds",
        duration: float = 30.0,
    ) -> str:
        output_file = output_path or str(OUTPUT_DIR / f"preview_{Path(audio_path).stem}.mp4")

        if background_path.endswith(('.png', '.jpg', '.jpeg')):
            bg_input = f"-loop 1 -i {background_path} -t {min(duration, 30)}"
        else:
            bg_input = f"-i {background_path} -t {min(duration, 30)}"

        filter_complex = RenderService._build_filter_complex(
            style, "preview", lyrics_path, min(duration, 30)
        )

        cmd = [
            'ffmpeg', '-y',
            *bg_input.split(),
            '-i', audio_path,
            '-filter_complex', filter_complex,
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '28',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-pix_fmt', 'yuv420p',
            '-r', str(AppConfig.preview_fps),
            '-s', AppConfig.preview_resolution,
            '-b:v', AppConfig.preview_bitrate,
            '-shortest',
            output_file
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Preview render failed with code {process.returncode}")

        return output_file

    @staticmethod
    async def render_full(
        audio_path: str,
        lyrics_path: str,
        background_path: str,
        output_path: str,
        style: str = "7clouds",
        resolution: str = "1920x1080",
        fps: int = 60,
        bitrate: str = "10M",
        progress_callback=None,
    ) -> str:
        output_file = output_path or str(OUTPUT_DIR / f"final_{Path(audio_path).stem}.mp4")

        audio_duration = await RenderService._get_duration(audio_path)
        total_frames = int(audio_duration * fps)

        if background_path.endswith(('.png', '.jpg', '.jpeg')):
            bg_input = f"-loop 1 -i {background_path}"
        else:
            bg_input = f"-i {background_path}"

        filter_complex = RenderService._build_filter_complex(
            style, "full", lyrics_path, audio_duration, fps
        )

        cmd = [
            'ffmpeg', '-y',
            *bg_input.split(),
            '-i', audio_path,
            '-filter_complex', filter_complex,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '18',
            '-c:a', 'aac',
            '-b:a', '320k',
            '-pix_fmt', 'yuv420p',
            '-r', str(fps),
            '-s', resolution,
            '-b:v', bitrate,
            '-maxrate', str(int(bitrate.replace('M', '')) * 2) + 'M',
            '-bufsize', str(int(bitrate.replace('M', '')) * 4) + 'M',
            '-shortest',
            '-movflags', '+faststart',
            output_file
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Full render failed with code {process.returncode}")

        return output_file

    @staticmethod
    async def _get_duration(file_path: str) -> float:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())

    @staticmethod
    def _build_filter_complex(style: str, mode: str, lyrics_path: str, duration: float, fps: int = 60) -> str:
        lrc_entries = []
        if lyrics_path.endswith('.lrc'):
            with open(lyrics_path) as f:
                lrc_entries = LyricsService.parse_lrc(f.read())
        elif lyrics_path.endswith('.srt'):
            with open(lyrics_path) as f:
                lrc_entries = LyricsService.parse_srt(f.read())

        if style == "7clouds":
            return RenderService._build_7clouds_style(lrc_entries, mode, fps)
        elif style == "minimal":
            return RenderService._build_minimal_style(lrc_entries, mode, fps)
        elif style == "kpop":
            return RenderService._build_kpop_style(lrc_entries, mode, fps)
        else:
            return RenderService._build_7clouds_style(lrc_entries, mode, fps)

    @staticmethod
    def _build_7clouds_style(entries: List[Dict], mode: str, fps: int) -> str:
        filters = [
            "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
            "gblur=sigma=20,colorbalance=rs=0.1:gs=0.1:bs=0.1[bg]",
            "[bg]drawbox=x=0:y=ih/2-100:w=iw:h=200:color=black@0.4:t=fill[bg_overlay]",
        ]

        current_filter = "[bg_overlay]"
        for i, entry in enumerate(entries):
            text = entry["text"].replace("'", "'").replace('"', '\\"')
            time = entry["time"]

            next_time = entries[i + 1]["time"] if i < len(entries) - 1 else time + 4

            if mode == "preview" and time > 30:
                break

            prev_text = entries[i - 1]["text"].replace("'", "'").replace('"', '\\"') if i > 0 else ""
            prev_time = entries[i - 1]["time"] if i > 0 else 0

            filter_name = f"lyric_{i}"
            filters.append(
                f"{current_filter}"
                f"drawtext=text='{text}':"
                f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"fontsize=48:fontcolor=white:"
                f"x=(w-text_w)/2:y=ih/2-30:"
                f"enable='between(t,{time},{next_time})':"
                f"borderw=2:bordercolor=black@0.5,"
                f"drawtext=text='{text}':"
                f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"fontsize=48:fontcolor=#00ff88:"
                f"x=(w-text_w)/2:y=ih/2-30:"
                f"enable='between(t,{time},{next_time})':"
                f"borderw=2:bordercolor=black@0.5[out_{i}]"
            )

            if prev_text:
                filters.append(
                    f"[out_{i}]drawtext=text='{prev_text}':"
                    f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
                    f"fontsize=32:fontcolor=white@0.5:"
                    f"x=(w-text_w)/2:y=ih/2-80:"
                    f"enable='between(t,{time},{next_time})':"
                    f"borderw=1:bordercolor=black@0.3[out2_{i}]"
                )
                current_filter = f"[out2_{i}]"
            else:
                current_filter = f"[out_{i}]"

        filters.append(f"{current_filter}null[vout]")
        return ";".join(filters)

    @staticmethod
    def _build_minimal_style(entries: List[Dict], mode: str, fps: int) -> str:
        filters = [
            "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
            "colorbalance=rs=-0.2:gs=-0.2:bs=-0.2[bg]",
        ]

        current_filter = "[bg]"
        for i, entry in enumerate(entries):
            text = entry["text"].replace("'", "'").replace('"', '\\"')
            time = entry["time"]
            next_time = entries[i + 1]["time"] if i < len(entries) - 1 else time + 4

            if mode == "preview" and time > 30:
                break

            filter_name = f"min_lyric_{i}"
            filters.append(
                f"{current_filter}"
                f"drawtext=text='{text}':"
                f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
                f"fontsize=36:fontcolor=white:"
                f"x=(w-text_w)/2:y=(h-text_h)/2:"
                f"enable='between(t,{time},{next_time})':"
                f"borderw=1:bordercolor=black@0.3[min_{i}]"
            )
            current_filter = f"[min_{i}]"

        filters.append(f"{current_filter}null[vout]")
        return ";".join(filters)

    @staticmethod
    def _build_kpop_style(entries: List[Dict], mode: str, fps: int) -> str:
        filters = [
            "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
            "colorbalance=rs=0.2:gs=0.1:bs=0.3,"
            "curves=all='0/0 0.5/0.6 1/1'[bg]",
            "[bg]drawbox=x=0:y=ih-300:w=iw:h=300:color=black@0.6:t=fill[bg_overlay]",
        ]

        current_filter = "[bg_overlay]"
        for i, entry in enumerate(entries):
            text = entry["text"].replace("'", "'").replace('"', '\\"')
            time = entry["time"]
            next_time = entries[i + 1]["time"] if i < len(entries) - 1 else time + 4

            if mode == "preview" and time > 30:
                break

            filters.append(
                f"{current_filter}"
                f"drawtext=text='{text}':"
                f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"fontsize=42:fontcolor=#ff69b4:"
                f"x=(w-text_w)/2:y=ih-200:"
                f"enable='between(t,{time},{next_time})':"
                f"borderw=2:bordercolor=black@0.5[k_{i}]"
            )
            current_filter = f"[k_{i}]"

        filters.append(f"{current_filter}null[vout]")
        return ";".join(filters)

    @staticmethod
    async def create_thumbnail(audio_path: str, title: str, artist: str, output_path: str) -> str:
        from PIL import Image, ImageDraw, ImageFont
        import textwrap

        img = Image.new('RGB', (1280, 720), (20, 20, 40))
        draw = ImageDraw.Draw(img)

        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            font_artist = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            font_title = ImageFont.load_default()
            font_artist = ImageFont.load_default()

        wrapped_title = textwrap.fill(title, width=20)
        bbox = draw.textbbox((0, 0), wrapped_title, font=font_title)
        tw = bbox[2] - bbox[0]
        draw.text(((1280 - tw) / 2, 200), wrapped_title, fill="white", font=font_title)

        if artist:
            bbox = draw.textbbox((0, 0), artist, font=font_artist)
            aw = bbox[2] - bbox[0]
            draw.text(((1280 - aw) / 2, 400), artist, fill="#00ff88", font=font_artist)

        draw.text((640, 600), "LyricLab", fill="gray", font=font_artist, anchor="mt")

        img.save(output_path)
        return output_path
