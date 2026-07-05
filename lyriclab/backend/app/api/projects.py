from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
from pathlib import Path
import json
import uuid
from app.database import query, execute
from app.models import ProjectCreate, ProjectUpdate
from app.agents.lyrics_agent import LyricsAgent
from app.agents.orchestrator import OrchestratorAgent
from app.config import AppConfig, DOWNLOADS_DIR

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("/")
async def list_projects(user_id: str):
    projects = query(
        "SELECT * FROM projects WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)
    )
    return {"projects": projects}

@router.get("/{project_id}")
async def get_project(project_id: str):
    projects = query("SELECT * FROM projects WHERE id=?", (project_id,))
    if not projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects[0]

@router.post("/")
async def create_project(project: ProjectCreate, user_id: str = "anonymous"):
    project_id = str(uuid.uuid4())
    execute("""
        INSERT INTO projects (id, user_id, title, artist, song_url, style, resolution, fps, bitrate, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (project_id, user_id, project.title, project.artist, project.song_url,
          project.style, project.resolution, project.fps, project.bitrate))
    return {"id": project_id, "status": "pending"}

@router.post("/process")
async def process_project(project_id: str, user_id: str = "anonymous"):
    projects = query("SELECT * FROM projects WHERE id=? AND user_id=?", (project_id, user_id))
    if not projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[0]
    result = await LyricsAgent.process_song(
        title=project["title"],
        artist=project.get("artist", ""),
        song_url=project.get("song_url", ""),
        audio_path=project.get("audio_path", ""),
        style=project.get("style", "7clouds"),
    )

    execute("""
        UPDATE projects SET audio_path=?, lyrics_path=?, background_path=?, status=?, metadata=?
        WHERE id=?
    """, (
        result.get("audio_path", ""), result.get("lyrics_path", ""),
        result.get("background_path", ""), result["status"],
        json.dumps(result), project_id,
    ))

    return result

@router.post("/preview")
async def preview_project(project_id: str, user_id: str = "anonymous"):
    projects = query("SELECT * FROM projects WHERE id=? AND user_id=?", (project_id, user_id))
    if not projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[0]
    result = await OrchestratorAgent._cmd_preview({"project_id": project_id}, user_id)
    return result

@router.post("/render")
async def render_project(project_id: str, user_id: str = "anonymous"):
    projects = query("SELECT * FROM projects WHERE id=? AND user_id=?", (project_id, user_id))
    if not projects:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await OrchestratorAgent._cmd_render({"project_id": project_id}, user_id)
    return result

@router.post("/upload")
async def upload_project(project_id: str, token_json: str = "", privacy: str = "public", user_id: str = "anonymous"):
    result = await OrchestratorAgent._cmd_upload({
        "project_id": project_id,
        "token_json": token_json,
        "privacy": privacy,
    }, user_id)
    return result

@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    filepath = DOWNLOADS_DIR / file.filename
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"path": str(filepath), "filename": file.filename}

@router.post("/upload-lyrics")
async def upload_lyrics(file: UploadFile = File(...)):
    filepath = DOWNLOADS_DIR / file.filename
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"path": str(filepath), "filename": file.filename}

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    execute("DELETE FROM projects WHERE id=?", (project_id,))
    return {"success": True}
