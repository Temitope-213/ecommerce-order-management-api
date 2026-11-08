from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    sku: str = Field(..., min_length=1, max_length=50)
    category_id: Optional[int] = Field(default=None, gt=0)


class ProductUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    sku: str = Field(..., min_length=1, max_length=50)
    category_id: Optional[int] = Field(default=None, gt=0)


class StockUpdate(BaseModel):
    stock: int = Field(..., ge=0)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int
    sku: str
    category_id: Optional[int] = None
    is_active: bool
    created_at: datetime


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int