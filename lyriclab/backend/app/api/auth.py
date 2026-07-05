from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.firebase_service import FirebaseService

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    id_token: str

class CreateUserRequest(BaseModel):
    email: str
    password: str

@router.post("/verify")
async def verify_token(req: LoginRequest):
    try:
        decoded = FirebaseService.verify_token(req.id_token)
        return {"success": True, "user": decoded}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/create")
async def create_user(req: CreateUserRequest):
    try:
        user = FirebaseService.create_user(req.email, req.password)
        return {"success": True, "user": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me/{uid}")
async def get_user(uid: str):
    try:
        user = FirebaseService.get_user(uid)
        return {"success": True, "user": user}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
