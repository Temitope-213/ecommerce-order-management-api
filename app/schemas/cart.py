from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class CartItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    name: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal
    stock: int
    is_active: bool


class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[CartItemResponse]
    total: Decimal