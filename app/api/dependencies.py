from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.use_cases.login_user import LoginUser
from app.application.use_cases.manage_categories import (
    CreateCategory,
    DeleteCategory,
    ListCategories,
    UpdateCategory,
)
from app.application.use_cases.manage_products import (
    CreateProduct,
    DeactivateProduct,
    GetProduct,
    ListProducts,
    UpdateProduct,
    UpdateStock,
)
from app.application.use_cases.register_user import RegisterUser
from app.core.security import decode_access_token
from app.domain.entities.user import User
from app.domain.repositories.category_repository import CategoryRepository
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.postgres_category_repository import (
    PostgresCategoryRepository,
)
from app.infrastructure.database.repositories.postgres_product_repository import (
    PostgresProductRepository,
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


def get_product_repository() -> ProductRepository:
    return PostgresProductRepository()


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


def create_product_use_case(
    products: ProductRepository = Depends(get_product_repository),
    categories: CategoryRepository = Depends(get_category_repository),
):
    return CreateProduct(products, categories)


def get_product_use_case(repo: ProductRepository = Depends(get_product_repository)):
    return GetProduct(repo)


def list_products_use_case(repo: ProductRepository = Depends(get_product_repository)):
    return ListProducts(repo)


def update_product_use_case(
    products: ProductRepository = Depends(get_product_repository),
    categories: CategoryRepository = Depends(get_category_repository),
):
    return UpdateProduct(products, categories)


def update_stock_use_case(repo: ProductRepository = Depends(get_product_repository)):
    return UpdateStock(repo)


def deactivate_product_use_case(repo: ProductRepository = Depends(get_product_repository)):
    return DeactivateProduct(repo)


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


def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    repo: UserRepository = Depends(get_user_repository),
) -> Optional[User]:
    # For public endpoints: a valid token is used if present, otherwise None
    if credentials is None:
        return None
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        return None
    return repo.get_by_id(user_id)