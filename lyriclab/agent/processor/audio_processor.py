#!/usr/bin/env python3
"""Audio processing utilities for LyricLab"""

import subprocess
import json
from pathlib import Path
from typing import Optional, Tuple

class AudioProcessor:
    @staticmethod
    def get_info(audio_path: str) -> dict:
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)

    @staticmethod
    def get_duration(audio_path: str) -> float:
        info = AudioProcessor.get_info(audio_path)
        return float(info.get('format', {}).get('duration', 0))

    @staticmethod
    def get_sample_rate(audio_path: str) -> int:
        info = AudioProcessor.get_info(audio_path)
        streams = info.get('streams', [])
        for stream in streams:
            if stream.get('codec_type') == 'audio':
                return int(stream.get('sample_rate', 44100))
        return 44100

    @staticmethod
    def normalize_audio(input_path: str, output_path: str) -> str:
        cmd = [
            'ffmpeg', '-i', input_path,
            '-af', 'loudnorm=I=-16:LRA=11:TP=-1.5',
            '-c:a', 'aac', '-b:a', '320k',
            '-y', output_path
        ]
        subprocess.run(cmd, capture_output=True)
        return output_path

    @staticmethod
    def extract_waveform(audio_path: str, output_path: str, width: int = 1920, height: int = 200) -> str:
        cmd = [
            'ffmpeg', '-i', audio_path,
            '-filter_complex',
            f'showwavespic=s={width}x{height}:colors=white|#6366f1',
            '-frames:v', '1',
            '-y', output_path
        ]
        subprocess.run(cmd, capture_output=True)
        return output_path

    @staticmethod
    def speed_change(input_path: str, speed: float, output_path: str) -> str:
        cmd = [
            'ffmpeg', '-i', input_path,
            '-af', f'atempo={speed}',
            '-y', output_path
        ]
        subprocess.run(cmd, capture_output=True)
        return output_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        info = AudioProcessor.get_info(sys.argv[1])
        print(json.dumps(info, indent=2))
