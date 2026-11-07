from fastapi import Depends

from app.application.use_cases.login_user import LoginUser
from app.application.use_cases.register_user import RegisterUser
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.postgres_user_repository import (
    PostgresUserRepository,
)


def get_user_repository() -> UserRepository:
    return PostgresUserRepository()


def register_user_use_case(repo: UserRepository = Depends(get_user_repository)):
    return RegisterUser(repo)


def login_user_use_case(repo: UserRepository = Depends(get_user_repository)):
    return LoginUser(repo)