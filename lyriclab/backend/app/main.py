from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from app.api import auth, projects, youtube, chat, trending, ollama, bulk
from app.database import init_db
from app.services.firebase_service import FirebaseService

app = FastAPI(
    title="LyricLab API",
    description="AI-Powered Lyrics Video Creator & Publisher",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(youtube.router)
app.include_router(chat.router)
app.include_router(trending.router)
app.include_router(ollama.router)
app.include_router(bulk.router)

@app.on_event("startup")
async def startup():
    init_db()
    FirebaseService.initialize()

    os.makedirs("/downloads", exist_ok=True)
    os.makedirs("/output", exist_ok=True)
    os.makedirs("/data", exist_ok=True)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "LyricLab",
    }

@app.get("/api/stats")
async def get_stats():
    from app.database import query
    projects = query("SELECT COUNT(*) as total FROM projects")[0]["total"]
    published = query("SELECT COUNT(*) as total FROM projects WHERE status='published'")[0]["total"]
    channels = query("SELECT COUNT(*) as total FROM youtube_channels")[0]["total"]
    return {
        "total_projects": projects,
        "published": published,
        "connected_channels": channels,
    }
