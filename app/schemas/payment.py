from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.payment import PaymentStatus


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    order_id: int
    amount: Decimal
    status: PaymentStatus
    rejection_reason: Optional[str] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None


class AdminPaymentResponse(PaymentResponse):
    user_id: Optional[int] = None
    order_status: Optional[str] = None
    reviewed_by: Optional[int] = None


class AdminPaymentListResponse(BaseModel):
    items: List[AdminPaymentResponse]
    total: int
    page: int
    page_size: int


class RejectPaymentRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)