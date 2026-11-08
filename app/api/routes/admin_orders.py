from typing import Optional

from fastapi import APIRouter, Depends, Path, Query

from app.api.dependencies import (
    admin_get_order_use_case,
    admin_list_orders_use_case,
    require_admin,
    update_order_status_use_case,
)
from app.application.use_cases.manage_orders import (
    AdminGetOrder,
    AdminListOrders,
    UpdateOrderStatus,
)
from app.domain.entities.order import OrderStatus
from app.domain.entities.user import User
from app.schemas.order import OrderListResponse, OrderResponse, OrderStatusUpdate

router = APIRouter(prefix="/admin/orders", tags=["Admin Operations"])


@router.get("", response_model=OrderListResponse)
def list_all_orders(
    order_status: Optional[OrderStatus] = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    use_case: AdminListOrders = Depends(admin_list_orders_use_case),
    admin: User = Depends(require_admin),
):
    items, total = use_case.execute(order_status, page, page_size)
    return OrderListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{order_id}", response_model=OrderResponse)
def get_any_order(
    order_id: int = Path(..., gt=0),
    use_case: AdminGetOrder = Depends(admin_get_order_use_case),
    admin: User = Depends(require_admin),
):
    return use_case.execute(order_id)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    data: OrderStatusUpdate,
    order_id: int = Path(..., gt=0),
    use_case: UpdateOrderStatus = Depends(update_order_status_use_case),
    admin: User = Depends(require_admin),
):
    return use_case.execute(order_id, data.status)