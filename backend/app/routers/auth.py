"""Admin authentication API router."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.auth_deps import (
    create_session_token,
    invalidate_token,
    verify_token,
    require_admin,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    status: str
    token: str
    message: str


@router.post("/login", response_model=LoginResponse)
async def admin_login(body: LoginRequest):
    """Authenticate with the admin secret password."""
    if body.password != settings.ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin password.")

    token = create_session_token()
    return LoginResponse(
        status="success",
        token=token,
        message="Admin session created successfully.",
    )


@router.get("/verify")
async def verify_session(token: str = Depends(require_admin)):
    """Check if the current Bearer token is still valid."""
    return {"status": "valid", "message": "Admin session is active."}


@router.post("/logout")
async def admin_logout(token: str = Depends(require_admin)):
    """Invalidate the current admin session."""
    invalidate_token(token)
    return {"status": "success", "message": "Admin session terminated."}
