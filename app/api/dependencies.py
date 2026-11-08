from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.use_cases.login_user import LoginUser
from app.application.use_cases.manage_categories import (
    CreateCategory,
    DeleteCategory,
    ListCategories,
    UpdateCategory,
)
from app.application.use_cases.register_user import RegisterUser
from app.core.security import decode_access_token
from app.domain.entities.user import User
from app.domain.repositories.category_repository import CategoryRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.postgres_category_repository import (
    PostgresCategoryRepository,
)
from app.infrastructure.database.repositories.postgres_user_repository import (
    PostgresUserRepository,
)

# Reads the "Authorization: Bearer <token>" header
bearer_scheme = HTTPBearer(auto_error=False)


# ---------- Repositories (the only place that chooses PostgreSQL) ----------
def get_user_repository() -> UserRepository:
    return PostgresUserRepository()


def get_category_repository() -> CategoryRepository:
    return PostgresCategoryRepository()


# ---------- Use cases ----------
def register_user_use_case(repo: UserRepository = Depends(get_user_repository)):
    return RegisterUser(repo)


def login_user_use_case(repo: UserRepository = Depends(get_user_repository)):
    return LoginUser(repo)


def create_category_use_case(repo: CategoryRepository = Depends(get_category_repository)):
    return CreateCategory(repo)


def list_categories_use_case(repo: CategoryRepository = Depends(get_category_repository)):
    return ListCategories(repo)


def update_category_use_case(repo: CategoryRepository = Depends(get_category_repository)):
    return UpdateCategory(repo)


def delete_category_use_case(repo: CategoryRepository = Depends(get_category_repository)):
    return DeleteCategory(repo)


# ---------- Guards ----------
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
    if credentials is None:
        raise unauthorized
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise unauthorized
    user = repo.get_by_id(user_id)
    if user is None:
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