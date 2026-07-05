#!/usr/bin/env python3
"""YouTube Crawler - Analyzes lyric video channels for style reference"""

import asyncio
import json
from typing import List, Dict, Optional
import httpx
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

YOUTUBE_API_KEY = "AIzaSyDbt70OPPr-teRTsPRf6lEsfRo6mOdSj-nU"
YOUTUBE_API = "https://www.googleapis.com/youtube/v3"

async def search_channels(query: str, max_results: int = 10) -> List[Dict]:
    """Search for lyric video channels"""
    url = f"{YOUTUBE_API}/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "channel",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            return []

        data = resp.json()
        channels = []
        for item in data.get("items", []):
            snippet = item["snippet"]
            channels.append({
                "channel_id": item["snippet"]["channelId"],
                "title": snippet["title"],
                "description": snippet.get("description", ""),
                "thumbnail": snippet["thumbnails"]["default"]["url"],
            })
        return channels

async def get_channel_videos(channel_id: str, max_results: int = 50) -> List[Dict]:
    """Get videos from a channel"""
    url = f"{YOUTUBE_API}/search"
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "type": "video",
        "order": "date",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            return []

        data = resp.json()
        videos = []
        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            videos.append({
                "video_id": video_id,
                "title": snippet["title"],
                "description": snippet.get("description", ""),
                "published_at": snippet["publishedAt"],
                "thumbnail": snippet["thumbnails"]["high"]["url"],
            })
        return videos

async def analyze_lyrics_channels():
    """Analyze popular lyric video channels"""
    queries = [
        "7clouds lyrics",
        "lyric video channel",
        "lyrics video",
        "music lyrics channel",
        "lyric videos",
    ]

    all_channels = []
    for query in queries:
        channels = await search_channels(query, 5)
        all_channels.extend(channels)

    seen = set()
    unique_channels = []
    for ch in all_channels:
        if ch["channel_id"] not in seen:
            seen.add(ch["channel_id"])
            unique_channels.append(ch)

    print(f"\nFound {len(unique_channels)} lyric video channels:\n")
    results = []
    for ch in unique_channels[:10]:
        print(f"  Channel: {ch['title']}")
        print(f"  ID: {ch['channel_id']}")
        videos = await get_channel_videos(ch["channel_id"], 5)
        print(f"  Recent videos: {len(videos)}")
        for v in videos[:3]:
            print(f"    - {v['title']}")
            results.append({"channel": ch["title"], "video": v})
        print()

    return results

if __name__ == "__main__":
    asyncio.run(analyze_lyrics_channels())
