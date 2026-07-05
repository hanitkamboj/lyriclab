from fastapi import APIRouter
from typing import Optional, List
from app.agents.research_agent import ResearchAgent
from app.database import query

router = APIRouter(prefix="/api/trending", tags=["trending"])

@router.get("/")
async def get_trending(platforms: str = "youtube,billboard", limit: int = 20):
    platform_list = platforms.split(",")
    results = await ResearchAgent.research_trending_songs(platform_list)
    return {"trending": results[:limit], "total": len(results[:limit])}

@router.get("/youtube")
async def youtube_trending(region: str = "US", max_results: int = 20):
    videos = await ResearchAgent.get_youtube_trending(region, max_results)
    return {"videos": videos}

@router.get("/channels")
async def trending_channels():
    channels = await ResearchAgent.get_trending_lyrics_channels()
    return {"channels": channels}

@router.get("/analyze/{video_id}")
async def analyze_video(video_id: str):
    style = await ResearchAgent.analyze_video_style(video_id)
    details = await ResearchAgent._get_video_details(video_id)
    return {"style": style, "details": details}

@router.get("/discover")
async def auto_discover():
    result = await ResearchAgent.auto_discover()
    return result
