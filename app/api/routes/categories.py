from typing import List

from fastapi import APIRouter, Depends, Path, Response, status

from app.api.dependencies import (
    create_category_use_case,
    delete_category_use_case,
    list_categories_use_case,
    require_admin,
    update_category_use_case,
)
from app.application.use_cases.manage_categories import (
    CreateCategory,
    DeleteCategory,
    ListCategories,
    UpdateCategory,
)
from app.domain.entities.user import User
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
def list_categories(use_case: ListCategories = Depends(list_categories_use_case)):
    return use_case.execute()


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    use_case: CreateCategory = Depends(create_category_use_case),
    admin: User = Depends(require_admin),  # admins only
):
    return use_case.execute(data.name, data.description)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    data: CategoryCreate,
    category_id: int = Path(..., gt=0),
    use_case: UpdateCategory = Depends(update_category_use_case),
    admin: User = Depends(require_admin),
):
    return use_case.execute(category_id, data.name, data.description)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int = Path(..., gt=0),
    use_case: DeleteCategory = Depends(delete_category_use_case),
    admin: User = Depends(require_admin),
):
    use_case.execute(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)