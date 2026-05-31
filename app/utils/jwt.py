from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from app.config import settings

def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

def verify_access_token(token: str) -> dict:
    try:
        payload: dict = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != "access":
            raise ValueError("Not an access token")
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token")

def verify_refresh_token(token: str) -> dict:
    try:
        payload: dict = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token")