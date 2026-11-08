from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class PaymentStatus(str, Enum):
    NOT_SUBMITTED = "NOT_SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class Payment:
    order_id: int
    amount: Decimal
    status: PaymentStatus
    receipt_path: str = ""
    rejection_reason: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    user_id: Optional[int] = None          # the customer who owns the order
    order_status: Optional[str] = None     # current status of the order
    id: Optional[int] = None