from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Tuple

from app.domain.entities.coupon import Coupon
from app.domain.exceptions import CouponNotFoundError, InvalidCouponError
from app.domain.repositories.coupon_repository import CouponRepository


def _as_utc(value: datetime) -> datetime:
    # A date sent without a timezone is treated as UTC
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _validate(
    code: str, discount_type: str, discount_value: Decimal,
    max_uses: int, min_order_amount: Decimal,
) -> None:
    if not code.strip():
        raise InvalidCouponError("Coupon code cannot be empty")
    if discount_type not in ("percentage", "fixed"):
        raise InvalidCouponError("discount_type must be 'percentage' or 'fixed'")
    if discount_value <= 0:
        raise InvalidCouponError("discount_value must be greater than 0")
    # Business rule: a percentage must be between 1 and 100
    if discount_type == "percentage" and discount_value > 100:
        raise InvalidCouponError("A percentage discount cannot be more than 100")
    if max_uses < 1:
        raise InvalidCouponError("max_uses must be at least 1")
    if min_order_amount < 0:
        raise InvalidCouponError("min_order_amount cannot be negative")


class CreateCoupon:
    def __init__(self, coupons: CouponRepository):
        self.coupons = coupons

    def execute(
        self, code: str, discount_type: str, discount_value: Decimal,
        expires_at: datetime, max_uses: int, min_order_amount: Decimal,
    ) -> Coupon:
        _validate(code, discount_type, discount_value, max_uses, min_order_amount)
        expires_at = _as_utc(expires_at)
        if expires_at <= datetime.now(timezone.utc):
            raise InvalidCouponError("The expiration date must be in the future")
        return self.coupons.create(
            Coupon(
                code=code.strip().upper(),   # codes are stored in uppercase
                discount_type=discount_type,
                discount_value=discount_value,
                expires_at=expires_at,
                max_uses=max_uses,
                min_order_amount=min_order_amount,
            )
        )


class ListCoupons:
    def __init__(self, coupons: CouponRepository):
        self.coupons = coupons

    def execute(self, page: int, page_size: int) -> Tuple[List[Coupon], int]:
        return self.coupons.list_all(page, page_size)


class GetCoupon:
    def __init__(self, coupons: CouponRepository):
        self.coupons = coupons

    def execute(self, coupon_id: int) -> Coupon:
        coupon = self.coupons.get_by_id(coupon_id)
        if coupon is None:
            raise CouponNotFoundError()
        return coupon


class UpdateCoupon:
    def __init__(self, coupons: CouponRepository):
        self.coupons = coupons

    def execute(
        self, coupon_id: int, code: str, discount_type: str, discount_value: Decimal,
        expires_at: datetime, max_uses: int, min_order_amount: Decimal, is_active: bool,
    ) -> Coupon:
        _validate(code, discount_type, discount_value, max_uses, min_order_amount)
        updated = self.coupons.update(
            coupon_id,
            Coupon(
                code=code.strip().upper(),
                discount_type=discount_type,
                discount_value=discount_value,
                expires_at=_as_utc(expires_at),
                max_uses=max_uses,
                min_order_amount=min_order_amount,
                is_active=is_active,
            ),
        )
        if updated is None:
            raise CouponNotFoundError()
        return updated


class DeactivateCoupon:
    def __init__(self, coupons: CouponRepository):
        self.coupons = coupons

    def execute(self, coupon_id: int) -> None:
        if not self.coupons.deactivate(coupon_id):
            raise CouponNotFoundError()