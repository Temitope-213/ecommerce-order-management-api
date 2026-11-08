from decimal import Decimal
from typing import Dict

from pydantic import BaseModel, ConfigDict


class SystemInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_customers: int
    total_admins: int
    total_products: int
    active_products: int
    low_stock_products: int
    total_orders: int
    orders_by_status: Dict[str, int]
    payments_under_review: int
    total_revenue: Decimal