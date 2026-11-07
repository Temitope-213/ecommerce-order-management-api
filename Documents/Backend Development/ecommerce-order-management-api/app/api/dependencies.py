from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.use_cases.login_user import LoginUser
from app.application.use_cases.register_user import RegisterUser
from app.core.security import decode_access_token
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.postgres_user_repository import (
    PostgresUserRepository,
)

# Reads the "Authorization: Bearer <token>" header
bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository() -> UserRepository:
    return PostgresUserRepository()


def register_user_use_case(repo: UserRepository = Depends(get_user_repository)):
    return RegisterUser(repo)


def login_user_use_case(repo: UserRepository = Depends(get_user_repository)):
    return LoginUser(repo)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    repo: UserRepository = Depends(get_user_repository),
) -> User:
    # Guard 1: authentication. One message for every failure.
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:  # no token was sent
        raise unauthorized
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:  # fake, tampered or expired token
        raise unauthorized
    user = repo.get_by_id(user_id)
    if user is None:  # the account no longer exists
        raise unauthorized
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    # Guard 2: authorization. The role comes from the database, never the client.
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator permission required",
        )
    return current_user