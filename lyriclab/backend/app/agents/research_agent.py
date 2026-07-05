import random
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import httpx
from bs4 import BeautifulSoup
from app.config import YouTubeConfig

class ResearchAgent:
    YOUTUBE_API = "https://www.googleapis.com/youtube/v3"

    @staticmethod
    async def get_youtube_trending(region: str = "US", max_results: int = 50) -> List[Dict]:
        url = f"{ResearchAgent.YOUTUBE_API}/videos"
        params = {
            "part": "snippet,statistics,contentDetails",
            "chart": "mostPopular",
            "regionCode": region,
            "maxResults": min(max_results, 50),
            "key": YouTubeConfig.api_key,
        }

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=params, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    videos = []
                    for item in data.get("items", []):
                        snippet = item.get("snippet", {})
                        videos.append({
                            "id": item["id"],
                            "title": snippet.get("title", ""),
                            "channel": snippet.get("channelTitle", ""),
                            "category_id": snippet.get("categoryId", ""),
                            "published_at": snippet.get("publishedAt", ""),
                            "view_count": item.get("statistics", {}).get("viewCount", 0),
                            "like_count": item.get("statistics", {}).get("likeCount", 0),
                            "duration": item.get("contentDetails", {}).get("duration", ""),
                        })
                    return videos
            except:
                pass
        return []

    @staticmethod
    async def search_youtube(query: str, max_results: int = 10, type: str = "video") -> List[Dict]:
        url = f"{ResearchAgent.YOUTUBE_API}/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": type,
            "maxResults": min(max_results, 50),
            "key": YouTubeConfig.api_key,
            "regionCode": "US",
        }

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=params, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    items = []
                    for item in data.get("items", []):
                        snippet = item.get("snippet", {})
                        items.append({
                            "id": item["id"].get("videoId", ""),
                            "title": snippet.get("title", ""),
                            "channel": snippet.get("channelTitle", ""),
                            "description": snippet.get("description", ""),
                            "published_at": snippet.get("publishedAt", ""),
                        })
                    return items
            except:
                pass
        return []

    @staticmethod
    async def get_trending_lyrics_channels(max_results: int = 20) -> List[Dict]:
        channels_query = [
            "lyric videos channel",
            "7clouds lyrics",
            "lyrics video",
            "lyric video channel",
            "music lyrics channel",
        ]

        all_results = []
        for query in channels_query:
            results = await ResearchAgent.search_youtube(query, max_results // len(channels_query))
            all_results.extend(results)

        return all_results[:max_results]

    @staticmethod
    async def get_channel_videos(channel_id: str, max_results: int = 50) -> List[Dict]:
        url = f"{ResearchAgent.YOUTUBE_API}/search"
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "type": "video",
            "order": "date",
            "maxResults": min(max_results, 50),
            "key": YouTubeConfig.api_key,
        }

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=params, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    return [{
                        "id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "published_at": item["snippet"]["publishedAt"],
                        "channel": item["snippet"]["channelTitle"],
                    } for item in data.get("items", [])]
            except:
                pass
        return []

    @staticmethod
    async def analyze_video_style(video_id: str) -> Dict[str, Any]:
        """Analyze a lyric video to extract style parameters"""
        video_details = await ResearchAgent._get_video_details(video_id)
        comments = await ResearchAgent._get_video_comments(video_id)

        style_indicators = {
            "has_dark_background": False,
            "uses_gradient": False,
            "lyric_position": "center",
            "font_size_estimate": "large",
            "has_album_art": False,
            "has_animations": False,
            "engagement_rate": 0,
        }

        if comments:
            style_keywords = {
                "dark": ["dark", "black", "night"],
                "gradient": ["gradient", "fade", "colorful"],
                "animated": ["animation", "moving", "kinetic"],
            }

        return style_indicators

    @staticmethod
    async def _get_video_details(video_id: str) -> Optional[Dict]:
        url = f"{ResearchAgent.YOUTUBE_API}/videos"
        params = {
            "part": "snippet,statistics,contentDetails,player",
            "id": video_id,
            "key": YouTubeConfig.api_key,
        }

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=params, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("items"):
                        return data["items"][0]
            except:
                pass
        return None

    @staticmethod
    async def _get_video_comments(video_id: str, max_results: int = 20) -> List[Dict]:
        url = f"{ResearchAgent.YOUTUBE_API}/commentThreads"
        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": min(max_results, 100),
            "key": YouTubeConfig.api_key,
        }

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=params, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    return [{
                        "text": item["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                        "likes": item["snippet"]["topLevelComment"]["snippet"]["likeCount"],
                    } for item in data.get("items", [])]
            except:
                pass
        return []

    @staticmethod
    async def research_trending_songs(platforms: List[str] = None) -> List[Dict]:
        if platforms is None:
            platforms = ["youtube", "billboard"]

        trending = []

        if "youtube" in platforms:
            yt_trending = await ResearchAgent.get_youtube_trending()
            for v in yt_trending[:20]:
                title = v.get("title", "")
                artist = v.get("channel", "")
                trending.append({
                    "title": title,
                    "artist": artist,
                    "source": "youtube",
                    "source_url": f"https://youtube.com/watch?v={v['id']}",
                    "rank": len(trending) + 1,
                    "views": v.get("view_count", 0),
                })

        if "billboard" in platforms:
            billboard = await ResearchAgent._scrape_billboard_hot100()
            for i, song in enumerate(billboard):
                trending.append({
                    "title": song.get("title", ""),
                    "artist": song.get("artist", ""),
                    "source": "billboard",
                    "source_url": song.get("url", ""),
                    "rank": i + 1,
                    "views": 0,
                })

        return trending[:50]

    @staticmethod
    async def _scrape_billboard_hot100() -> List[Dict]:
        songs = []
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get("https://www.billboard.com/charts/hot-100/", timeout=15)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    for item in soup.select('.o-chart-results-list-row-container'):
                        title_el = item.select_one('.c-title')
                        artist_el = item.select_one('.c-label')
                        if title_el and artist_el:
                            songs.append({
                                "title": title_el.get_text(strip=True),
                                "artist": artist_el.get_text(strip=True),
                            })
            except:
                pass
        return songs

    @staticmethod
    async def auto_discover() -> Dict[str, Any]:
        """Full auto-discovery pipeline"""
        trending = await ResearchAgent.research_trending_songs()
        channels = await ResearchAgent.get_trending_lyrics_channels()

        style_videos = []
        for channel in channels[:5]:
            videos = await ResearchAgent.get_channel_videos(channel.get("id", ""), 5)
            style_videos.extend(videos)

        return {
            "trending_songs": trending,
            "similar_channels": channels[:10],
            "style_references": style_videos[:20],
            "discovered_at": datetime.now().isoformat(),
        }
