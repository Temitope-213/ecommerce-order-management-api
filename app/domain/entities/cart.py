from dataclasses import dataclass, field
from decimal import Decimal
from typing import List


@dataclass
class CartItem:
    product_id: int
    name: str
    unit_price: Decimal
    quantity: int
    stock: int
    is_active: bool = True

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Cart:
    user_id: int
    items: List[CartItem] = field(default_factory=list)

    @property
    def total(self) -> Decimal:
        return sum((item.line_total for item in self.items), Decimal("0"))