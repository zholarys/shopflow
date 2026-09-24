from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.services.auth import decode_token

bearer = HTTPBearer(auto_error=False)

async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    error = HTTPException(status_code=401, detail="Invalid or missing credentials",
                          headers={"WWW-Authenticate": "Bearer"})
    if credentials is None:
        raise error
    payload = decode_token(credentials.credentials)
    try:
        user_id = int(payload["sub"])
    except (TypeError, KeyError, ValueError):
        raise error
    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise error
    return user

async def admin_user(user: User = Depends(current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
