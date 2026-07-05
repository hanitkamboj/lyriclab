from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.agents.orchestrator import OrchestratorAgent
from app.agents.research_agent import ResearchAgent
from app.database import query, execute
import json
import uuid

router = APIRouter(prefix="/api/bulk", tags=["bulk"])

class BulkJobRequest(BaseModel):
    user_id: str
    items: List[Dict[str, Any]]
    auto_upload: bool = False
    privacy: str = "public"

@router.post("/create")
async def create_bulk_jobs(req: BulkJobRequest, background_tasks: BackgroundTasks):
    result = await OrchestratorAgent._cmd_bulk({
        "items": req.items,
        "auto_mode": req.auto_upload,
    }, req.user_id)

    return result

@router.post("/auto")
async def start_auto_mode(user_id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(OrchestratorAgent._auto_discover_and_process, user_id)
    return {"success": True, "message": "Auto mode started"}

@router.post("/from-trending")
async def create_from_trending(user_id: str, count: int = 10, auto_upload: bool = False):
    trending = await ResearchAgent.research_trending_songs()
    items = [{
        "title": s["title"],
        "artist": s.get("artist", ""),
        "song_url": s.get("source_url", ""),
    } for s in trending[:count]]

    result = await OrchestratorAgent._cmd_bulk({
        "items": items,
        "auto_mode": auto_upload,
    }, user_id)

    return result

@router.get("/status/{user_id}")
async def get_bulk_status(user_id: str):
    projects = query(
        "SELECT id, title, status, created_at, youtube_status FROM projects WHERE user_id=? AND is_bulk_item=1 ORDER BY created_at DESC",
        (user_id,)
    )
    return {
        "projects": projects,
        "total": len(projects),
        "completed": sum(1 for p in projects if p["status"] == "published"),
        "processing": sum(1 for p in projects if p["status"] in ("processing", "rendering")),
        "failed": sum(1 for p in projects if p["status"].endswith("failed")),
    }

@router.get("/groups/{user_id}")
async def get_bulk_groups(user_id: str):
    groups = query("""
        SELECT bulk_group_id, COUNT(*) as count,
               SUM(CASE WHEN status='published' THEN 1 ELSE 0 END) as completed,
               MIN(created_at) as started_at
        FROM projects WHERE user_id=? AND bulk_group_id IS NOT NULL
        GROUP BY bulk_group_id
        ORDER BY started_at DESC
    """, (user_id,))
    return {"groups": groups}
