from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.domain.entities.payment import Payment, PaymentStatus


class PaymentRepository(ABC):
    @abstractmethod
    def create_submission(self, order_id: int, user_id: int, receipt_path: str) -> Payment:
        """Records a new proof of payment (UNDER_REVIEW) in one transaction."""

    @abstractmethod
    def get_latest_for_order(self, order_id: int) -> Optional[Payment]: ...

    @abstractmethod
    def get_by_id(self, payment_id: int) -> Optional[Payment]: ...

    @abstractmethod
    def list_all(
        self, status: Optional[PaymentStatus], page: int, page_size: int
    ) -> Tuple[List[Payment], int]: ...

    @abstractmethod
    def review(
        self, payment_id: int, admin_id: int, approve: bool, reason: Optional[str]
    ) -> Payment:
        """Approves or rejects in one transaction. Approving confirms the order."""

    @abstractmethod
    def has_approved_payment(self, order_id: int) -> bool: ...