from datetime import datetime
from decimal import Decimal
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field


class CouponCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    code: str = Field(..., min_length=3, max_length=50)
    discount_type: Literal["percentage", "fixed"]
    discount_value: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    expires_at: datetime
    max_uses: int = Field(..., ge=1)
    min_order_amount: Decimal = Field(
        default=Decimal("0"), ge=0, max_digits=10, decimal_places=2
    )


class CouponUpdate(CouponCreate):
    is_active: bool = True


class CouponResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    discount_type: str
    discount_value: Decimal
    expires_at: datetime
    max_uses: int
    times_used: int
    min_order_amount: Decimal
    is_active: bool
    created_at: datetime


class CouponListResponse(BaseModel):
    items: List[CouponResponse]
    total: int
    page: int
    page_size: int