from decimal import Decimal
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.api.dependencies import (
    create_product_use_case,
    deactivate_product_use_case,
    get_optional_user,
    get_product_use_case,
    list_products_use_case,
    require_admin,
    update_product_use_case,
    update_stock_use_case,
)
from app.application.use_cases.manage_products import (
    CreateProduct,
    DeactivateProduct,
    GetProduct,
    ListProducts,
    UpdateProduct,
    UpdateStock,
)
from app.domain.entities.user import User
from app.domain.repositories.product_repository import ProductFilters
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
    StockUpdate,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    search: Optional[str] = Query(default=None, max_length=100),
    category_id: Optional[int] = Query(default=None, gt=0),
    min_price: Optional[Decimal] = Query(default=None, ge=0),
    max_price: Optional[Decimal] = Query(default=None, ge=0),
    sort_by: Literal["price", "created_at"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    use_case: ListProducts = Depends(list_products_use_case),
    user: Optional[User] = Depends(get_optional_user),
):
    filters = ProductFilters(
        search=search, category_id=category_id,
        min_price=min_price, max_price=max_price,
        sort_by=sort_by, order=order, page=page, page_size=page_size,
        include_inactive=bool(user and user.is_admin),
    )
    items, total = use_case.execute(filters)
    return ProductListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int = Path(..., gt=0),
    use_case: GetProduct = Depends(get_product_use_case),
    user: Optional[User] = Depends(get_optional_user),
):
    return use_case.execute(product_id, is_admin=bool(user and user.is_admin))


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    use_case: CreateProduct = Depends(create_product_use_case),
    admin: User = Depends(require_admin),
):
    return use_case.execute(
        data.name, data.price, data.sku, data.stock, data.description, data.category_id
    )


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    data: ProductUpdate,
    product_id: int = Path(..., gt=0),
    use_case: UpdateProduct = Depends(update_product_use_case),
    admin: User = Depends(require_admin),
):
    return use_case.execute(
        product_id, data.name, data.price, data.sku, data.description, data.category_id
    )


@router.patch("/{product_id}/stock", response_model=ProductResponse)
def update_stock(
    data: StockUpdate,
    product_id: int = Path(..., gt=0),
    use_case: UpdateStock = Depends(update_stock_use_case),
    admin: User = Depends(require_admin),
):
    return use_case.execute(product_id, data.stock)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_product(
    product_id: int = Path(..., gt=0),
    use_case: DeactivateProduct = Depends(deactivate_product_use_case),
    admin: User = Depends(require_admin),
):
    use_case.execute(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)