"""Admin authentication dependencies.

Provides a `require_admin` FastAPI dependency that validates Bearer tokens
issued by the /api/auth/login endpoint.
"""

import secrets
import time
from typing import Dict, Tuple

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings

# In-memory session store: token -> expiry_timestamp
_active_sessions: Dict[str, float] = {}

security = HTTPBearer(auto_error=False)


def create_session_token() -> str:
    """Generate a cryptographically secure session token and store it."""
    token = secrets.token_urlsafe(32)
    expiry = time.time() + settings.ADMIN_TOKEN_EXPIRY_HOURS * 3600
    _active_sessions[token] = expiry
    _cleanup_expired()
    return token


def invalidate_token(token: str) -> bool:
    """Remove a token from the session store."""
    return _active_sessions.pop(token, None) is not None


def verify_token(token: str) -> bool:
    """Check if a token is valid and not expired."""
    expiry = _active_sessions.get(token)
    if expiry is None:
        return False
    if time.time() > expiry:
        _active_sessions.pop(token, None)
        return False
    return True


def _cleanup_expired():
    """Remove expired tokens from the store."""
    now = time.time()
    expired = [t for t, exp in _active_sessions.items() if now > exp]
    for t in expired:
        _active_sessions.pop(t, None)


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """FastAPI dependency — raises 401/403 if the request is not from an admin.

    Returns the validated token string.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in as admin.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired admin session. Please log in again.",
        )

    return token
