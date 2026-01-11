from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.config import get_settings
from app.schemas.common import TokenData, TokenPayload

settings = get_settings()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(data: TokenData, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.model_dump()
    to_encode["type"] = "access"
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def create_refresh_token(data: TokenData, expires_delta: timedelta | None = None) -> str:
    """Create a JWT refresh token."""
    to_encode = data.model_dump()
    to_encode["type"] = "refresh"
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.jwt_refresh_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_access_token(token: str) -> TokenPayload | None:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        token_payload = TokenPayload(**payload)
        if token_payload.type != "access":
            return None
        return token_payload
    except jwt.PyJWTError:
        return None


def decode_refresh_token(token: str) -> TokenPayload | None:
    """Decode and verify a JWT refresh token."""
    try:
        payload = jwt.decode(
            token, settings.jwt_refresh_secret_key, algorithms=[settings.jwt_algorithm]
        )
        token_payload = TokenPayload(**payload)
        if token_payload.type != "refresh":
            return None
        return token_payload
    except jwt.PyJWTError:
        return None
