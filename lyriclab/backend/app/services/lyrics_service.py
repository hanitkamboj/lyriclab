import re
import json
import asyncio
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import httpx
from bs4 import BeautifulSoup

class LyricsService:
    LRCLIB_API = "https://lrclib.net/api"

    @staticmethod
    async def search_lrclib(track_name: str, artist_name: str = "") -> Optional[Dict]:
        async with httpx.AsyncClient() as client:
            try:
                params = {"track_name": track_name, "artist_name": artist_name} if artist_name else {"q": track_name}
                resp = await client.get(f"{LyricsService.LRCLIB_API}/search", params=params, timeout=10)
                if resp.status_code == 200:
                    results = resp.json()
                    if results:
                        return results[0]
            except:
                pass
        return None

    @staticmethod
    async def get_lrc_from_lrclib(track_name: str, artist_name: str = "") -> Optional[str]:
        result = await LyricsService.search_lrclib(track_name, artist_name)
        if result and result.get("syncedLyrics"):
            return result["syncedLyrics"]
        return None

    @staticmethod
    async def fetch_from_azlyrics(track_name: str, artist: str = "") -> Optional[str]:
        search_url = f"https://search.azlyrics.com/search.php?q={track_name.replace(' ', '+')}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(search_url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    links = soup.select('a[href*="azlyrics.com/lyrics/"]')
                    if links:
                        lyric_url = links[0]['href']
                        lyric_resp = await client.get(lyric_url, headers=headers, timeout=10)
                        if lyric_resp.status_code == 200:
                            lyric_soup = BeautifulSoup(lyric_resp.text, 'html.parser')
                            divs = lyric_soup.find_all('div', class_=None)
                            for div in divs:
                                text = div.get_text(strip=True)
                                if len(text) > 100:
                                    return text
            except:
                pass
        return None

    @staticmethod
    async def create_lrc_from_plain(plain_lyrics: str, duration: float) -> str:
        lines = [l.strip() for l in plain_lyrics.split('\n') if l.strip()]
        if not lines:
            return ""

        lrc_lines = []
        time_per_line = duration / len(lines)

        for i, line in enumerate(lines):
            minutes = int((i * time_per_line) // 60)
            seconds = (i * time_per_line) % 60
            lrc_lines.append(f"[{minutes:02d}:{seconds:05.2f}]{line}")

        lrc_lines.append(f"[{int(duration)//60:02d}:{duration%60:05.2f}]")
        return '\n'.join(lrc_lines)

    @staticmethod
    def parse_lrc(lrc_content: str) -> List[Dict]:
        pattern = r'\[(\d{2}):(\d{2}(?:\.\d{2})?)\](.*)'
        entries = []

        for line in lrc_content.split('\n'):
            match = re.match(pattern, line)
            if match:
                minutes = int(match.group(1))
                seconds = float(match.group(2))
                text = match.group(3).strip()
                timestamp = minutes * 60 + seconds
                entries.append({"time": timestamp, "text": text})

        return sorted(entries, key=lambda x: x["time"])

    @staticmethod
    def parse_srt(srt_content: str) -> List[Dict]:
        entries = []
        pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n((?:.+\n?)*)'

        for match in re.finditer(pattern, srt_content):
            start = match.group(2)
            text = match.group(4).strip().replace('\n', ' ')
            h, m, s = start.split(':')
            timestamp = int(h) * 3600 + int(m) * 60 + float(s.replace(',', '.'))
            entries.append({"time": timestamp, "text": text})

        return entries

    @staticmethod
    async def generate_from_url(song_url: str) -> Tuple[Optional[str], Optional[str]]:
        """Try to extract lyrics from various sources. Returns (lrc_content, source)"""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(song_url, timeout=10, follow_redirects=True)
                html = resp.text

                soup = BeautifulSoup(html, 'html.parser')

                lyrics_div = soup.find('div', class_=re.compile(r'lyrics', re.I))
                if lyrics_div:
                    return lyrics_div.get_text(strip=True), "web"

                for script in soup.find_all('script'):
                    if 'lyrics' in script.text.lower() or 'lyric' in script.text.lower():
                        return script.text, "script"
            except:
                pass

        return None, None

    @staticmethod
    async def verify_timing(lrc_entries: List[Dict], audio_duration: float) -> bool:
        if not lrc_entries:
            return False
        last_time = lrc_entries[-1]["time"]
        if last_time > audio_duration + 5:
            return False
        for i in range(len(lrc_entries) - 1):
            if lrc_entries[i+1]["time"] - lrc_entries[i]["time"] < 0.1:
                return False
        return True
