from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.api.dependencies import (
    create_coupon_use_case,
    deactivate_coupon_use_case,
    get_coupon_use_case,
    list_coupons_use_case,
    require_admin,
    update_coupon_use_case,
)
from app.application.use_cases.manage_coupons import (
    CreateCoupon,
    DeactivateCoupon,
    GetCoupon,
    ListCoupons,
    UpdateCoupon,
)
from app.domain.entities.user import User
from app.schemas.coupon import (
    CouponCreate,
    CouponListResponse,
    CouponResponse,
    CouponUpdate,
)

# Every coupon route is admin only. Customers only ever send a coupon_code at checkout.
router = APIRouter(prefix="/admin/coupons", tags=["Coupons"])


@router.post("", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(
    data: CouponCreate,
    use_case: CreateCoupon = Depends(create_coupon_use_case),
    admin: User = Depends(require_admin),
):
    return use_case.execute(
        data.code, data.discount_type, data.discount_value,
        data.expires_at, data.max_uses, data.min_order_amount,
    )


@router.get("", response_model=CouponListResponse)
def list_coupons(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    use_case: ListCoupons = Depends(list_coupons_use_case),
    admin: User = Depends(require_admin),
):
    items, total = use_case.execute(page, page_size)
    return CouponListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{coupon_id}", response_model=CouponResponse)
def get_coupon(
    coupon_id: int = Path(..., gt=0),
    use_case: GetCoupon = Depends(get_coupon_use_case),
    admin: User = Depends(require_admin),
):
    return use_case.execute(coupon_id)


@router.put("/{coupon_id}", response_model=CouponResponse)
def update_coupon(
    data: CouponUpdate,
    coupon_id: int = Path(..., gt=0),
    use_case: UpdateCoupon = Depends(update_coupon_use_case),
    admin: User = Depends(require_admin),
):
    return use_case.execute(
        coupon_id, data.code, data.discount_type, data.discount_value,
        data.expires_at, data.max_uses, data.min_order_amount, data.is_active,
    )


@router.delete("/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_coupon(
    coupon_id: int = Path(..., gt=0),
    use_case: DeactivateCoupon = Depends(deactivate_coupon_use_case),
    admin: User = Depends(require_admin),
):
    use_case.execute(coupon_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)