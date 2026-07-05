from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
from app.database import query, execute
import uuid

router = APIRouter(prefix="/api/ollama", tags=["ollama"])

class OllamaRequest(BaseModel):
    model: str = "llama3.1"
    prompt: str
    system: Optional[str] = None
    base_url: str = "http://localhost:11434"
    stream: bool = False

class OllamaConfigRequest(BaseModel):
    user_id: str
    name: str
    base_url: str
    model_name: str
    set_active: bool = True

@router.post("/chat")
async def chat_with_ollama(req: OllamaRequest):
    url = f"{req.base_url}/api/generate"
    payload = {
        "model": req.model,
        "prompt": req.prompt,
        "stream": req.stream,
    }
    if req.system:
        payload["system"] = req.system

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                return resp.json()
            else:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail=f"Cannot connect to Ollama at {req.base_url}")

@router.post("/config")
async def save_ollama_config(req: OllamaConfigRequest):
    config_id = str(uuid.uuid4())

    if req.set_active:
        execute("UPDATE ollama_configs SET is_active=0 WHERE user_id=?", (req.user_id,))

    execute("""
        INSERT INTO ollama_configs (id, user_id, name, base_url, model_name, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (config_id, req.user_id, req.name, req.base_url, req.model_name, 1 if req.set_active else 0))

    return {"id": config_id, "success": True}

@router.get("/configs/{user_id}")
async def get_ollama_configs(user_id: str):
    configs = query("SELECT * FROM ollama_configs WHERE user_id=? ORDER BY is_active DESC", (user_id,))
    return {"configs": configs}

@router.get("/active/{user_id}")
async def get_active_config(user_id: str):
    configs = query("SELECT * FROM ollama_configs WHERE user_id=? AND is_active=1", (user_id,))
    if configs:
        return {"config": configs[0]}
    return {"config": None}

@router.delete("/config/{config_id}")
async def delete_config(config_id: str):
    execute("DELETE FROM ollama_configs WHERE id=?", (config_id,))
    return {"success": True}
