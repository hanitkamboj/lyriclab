from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

def gen_id():
    return str(uuid.uuid4())

class ProjectCreate(BaseModel):
    title: str
    artist: Optional[str] = ""
    song_url: Optional[str] = ""
    style: str = "7clouds"
    resolution: str = "1920x1080"
    fps: int = 60
    bitrate: str = "10M"

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    status: Optional[str] = None
    song_url: Optional[str] = None
    audio_path: Optional[str] = None
    lyrics_path: Optional[str] = None
    background_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    style: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    visibility: Optional[str] = None

class YouTubeChannelCreate(BaseModel):
    channel_name: str
    channel_id: str
    access_token: str
    refresh_token: str

class JobCreate(BaseModel):
    project_id: str
    job_type: str
    priority: int = 0
    metadata: Dict[str, Any] = {}

class ChatMessage(BaseModel):
    role: str
    content: str
    session_id: Optional[str] = None

class OllamaConfigCreate(BaseModel):
    name: str
    base_url: str
    model_name: str

class BulkCreate(BaseModel):
    items: List[Dict[str, Any]]
    auto_mode: bool = False

class AgentCommand(BaseModel):
    command: str
    params: Dict[str, Any] = {}
