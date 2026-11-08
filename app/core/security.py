from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import JWT_SECRET_KEY

ALGORITHM = "HS256"  # the signing method
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # a token stops working after 30 minutes

password_hash = PasswordHash.recommended()  # Argon2, a strong hashing method


def _get_secret() -> str:
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is not configured")
    return JWT_SECRET_KEY


def hash_password(password: str) -> str:
    # Scramble the password so the real one is never stored
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Check a typed password against the stored scrambled version
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    # Build a signed token holding the user's ID and an expiry time
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, _get_secret(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[int]:
    # Return the user's ID if the token is genuine and not expired, else None
    try:
        payload = jwt.decode(
            token,
            _get_secret(),
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        return int(payload["sub"])
    except (InvalidTokenError, ValueError, KeyError):
        return None