from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from app.domain.exceptions import InvalidStatusTransitionError


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


# Business rule: which status changes are allowed
ALLOWED_TRANSITIONS = {
    OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
    OrderStatus.PROCESSING: {OrderStatus.SHIPPED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}


def ensure_transition(current: OrderStatus, new: OrderStatus) -> None:
    if new not in ALLOWED_TRANSITIONS[current]:
        raise InvalidStatusTransitionError(
            f"Cannot change order status from {current.value} to {new.value}"
        )


@dataclass
class OrderItem:
    product_name: str
    unit_price: Decimal
    quantity: int
    product_id: Optional[int] = None
    id: Optional[int] = None

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Order:
    user_id: int
    status: OrderStatus
    subtotal: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    items: List[OrderItem] = field(default_factory=list)
    coupon_id: Optional[int] = None
    idempotency_key: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None