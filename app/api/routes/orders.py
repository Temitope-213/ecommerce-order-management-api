from fastapi import APIRouter, Depends, Header, Path, Query, Response, status

from app.api.dependencies import (
    cancel_my_order_use_case,
    checkout_use_case,
    get_current_user,
    get_my_order_use_case,
    list_my_orders_use_case,
)
from app.application.use_cases.manage_orders import (
    CancelMyOrder,
    Checkout,
    GetMyOrder,
    ListMyOrders,
)
from app.domain.entities.user import User
from app.schemas.order import OrderListResponse, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    response: Response,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=100),
    use_case: Checkout = Depends(checkout_use_case),
    current_user: User = Depends(get_current_user),
):
    order, created = use_case.execute(current_user.id, idempotency_key)
    if not created:
        # Same key sent again: nothing new was created, return the original order
        response.status_code = status.HTTP_200_OK
    return order


@router.get("", response_model=OrderListResponse)
def my_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    use_case: ListMyOrders = Depends(list_my_orders_use_case),
    current_user: User = Depends(get_current_user),
):
    items, total = use_case.execute(current_user.id, page, page_size)
    return OrderListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int = Path(..., gt=0),
    use_case: GetMyOrder = Depends(get_my_order_use_case),
    current_user: User = Depends(get_current_user),
):
    return use_case.execute(current_user.id, order_id)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int = Path(..., gt=0),
    use_case: CancelMyOrder = Depends(cancel_my_order_use_case),
    current_user: User = Depends(get_current_user),
):
    return use_case.execute(current_user.id, order_id)