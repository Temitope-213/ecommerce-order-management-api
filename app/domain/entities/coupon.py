from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional


@dataclass
class Coupon:
    code: str
    discount_type: str          # "percentage" or "fixed"
    discount_value: Decimal
    expires_at: datetime
    max_uses: int
    min_order_amount: Decimal = Decimal("0")
    is_active: bool = True
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    times_used: int = 0


def calculate_discount(discount_type: str, discount_value: Decimal, subtotal: Decimal) -> Decimal:
    """Business rule: the discount can never be more than the subtotal,
    so the final total can never be negative."""
    if discount_type == "percentage":
        discount = (subtotal * discount_value / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    else:
        discount = discount_value
    return min(discount, subtotal)