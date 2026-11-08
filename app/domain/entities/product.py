from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Product:
    name: str
    price: Decimal
    sku: str
    stock: int = 0
    description: Optional[str] = None
    category_id: Optional[int] = None
    is_active: bool = True
    id: Optional[int] = None
    created_at: Optional[datetime] = None