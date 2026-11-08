from dataclasses import dataclass
from decimal import Decimal
from typing import Dict


@dataclass
class SystemInfo:
    total_customers: int
    total_admins: int
    total_products: int
    active_products: int
    low_stock_products: int          # active products with 5 or fewer units left
    total_orders: int
    orders_by_status: Dict[str, int]
    payments_under_review: int
    total_revenue: Decimal           # orders that are confirmed or further along