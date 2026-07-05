from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import uuid
from app.services.youtube_service import YouTubeService
from app.database import query, execute

router = APIRouter(prefix="/api/youtube", tags=["youtube"])

class ConnectRequest(BaseModel):
    auth_code: str
    user_id: str

class ChannelSaveRequest(BaseModel):
    user_id: str
    channel_name: str
    channel_id: str
    access_token: str
    refresh_token: str

@router.get("/auth-url")
async def get_auth_url():
    flow = YouTubeService.get_oauth_flow()
    auth_url, _ = flow.authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent")
    return {"auth_url": auth_url}

@router.post("/connect")
async def connect_youtube(req: ConnectRequest):
    try:
        flow = YouTubeService.get_oauth_flow()
        flow.fetch_token(code=req.auth_code)
        creds = flow.credentials
        token_data = {"token": creds.token, "refresh_token": creds.refresh_token, "token_uri": creds.token_uri,
                      "client_id": creds.client_id, "client_secret": creds.client_secret, "scopes": creds.scopes}
        channel_info = await YouTubeService.get_channel_info(json.dumps(token_data))
        channel_id = str(uuid.uuid4())
        execute("INSERT INTO youtube_channels (id, user_id, channel_name, channel_id, access_token, refresh_token) VALUES (?, ?, ?, ?, ?, ?)",
                (channel_id, req.user_id, channel_info.get("title", ""), channel_info.get("channel_id", ""),
                 creds.token, creds.refresh_token or ""))
        return {"success": True, "channel": channel_info, "token_json": json.dumps(token_data)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/channels/{user_id}")
async def get_channels(user_id: str):
    channels = query("SELECT * FROM youtube_channels WHERE user_id=?", (user_id,))
    return {"channels": channels}

@router.delete("/channels/{channel_id}")
async def disconnect_channel(channel_id: str):
    execute("DELETE FROM youtube_channels WHERE id=?", (channel_id,))
    return {"success": True}

@router.get("/verify/{video_id}")
async def verify_video(video_id: str, token_json: str = ""):
    try:
        exists = await YouTubeService.check_video_exists(token_json, video_id)
        return {"exists": exists}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/seo")
async def generate_seo(title: str, artist: str = "", tags: str = ""):
    tag_list = json.loads(tags) if tags else []
    seo = YouTubeService.generate_seo_metadata(title, artist, tag_list)
    return seo
