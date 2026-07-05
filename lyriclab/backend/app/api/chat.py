from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.agents.orchestrator import OrchestratorAgent
from app.database import query, execute
import uuid
import json

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"
    session_id: Optional[str] = None
    params: Dict[str, Any] = {}

@router.post("/")
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    # Store user message
    execute("""
        INSERT INTO chat_history (id, user_id, role, content, session_id)
        VALUES (?, ?, 'user', ?, ?)
    """, (str(uuid.uuid4()), req.user_id, req.message, session_id))

    # Parse command
    parts = req.message.strip().split()
    command = parts[0].lower() if parts else "help"
    params = req.params

    # Extract params from message
    if len(parts) > 1:
        for part in parts[1:]:
            if "=" in part:
                key, val = part.split("=", 1)
                params[key] = val

    result = await OrchestratorAgent.handle_chat_command(command, params, req.user_id)

    # Store assistant response
    execute("""
        INSERT INTO chat_history (id, user_id, role, content, session_id)
        VALUES (?, ?, 'assistant', ?, ?)
    """, (str(uuid.uuid4()), req.user_id, json.dumps(result), session_id))

    return {
        "response": result,
        "session_id": session_id,
    }

@router.get("/history/{user_id}")
async def get_history(user_id: str, session_id: Optional[str] = None):
    if session_id:
        messages = query(
            "SELECT role, content, timestamp FROM chat_history WHERE user_id=? AND session_id=? ORDER BY timestamp",
            (user_id, session_id)
        )
    else:
        messages = query(
            "SELECT role, content, timestamp, session_id FROM chat_history WHERE user_id=? ORDER BY timestamp DESC LIMIT 50",
            (user_id,)
        )
    return {"messages": messages}

@router.get("/sessions/{user_id}")
async def get_sessions(user_id: str):
    sessions = query("""
        SELECT DISTINCT session_id, MIN(timestamp) as created_at, MAX(timestamp) as last_message
        FROM chat_history WHERE user_id=?
        GROUP BY session_id
        ORDER BY last_message DESC
    """, (user_id,))
    return {"sessions": sessions}
