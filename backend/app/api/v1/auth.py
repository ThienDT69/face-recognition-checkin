from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(credentials: LoginRequest):
    """Login endpoint (simplified - implement your auth logic)"""
    # TODO: Implement proper JWT authentication
    return {
        "access_token": "dummy_token",
        "token_type": "bearer"
    }
