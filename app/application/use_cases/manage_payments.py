from decimal import Decimal
from typing import List, Optional, Tuple

from app.domain.entities.payment import Payment, PaymentStatus
from app.domain.exceptions import (
    InvalidPaymentStateError,
    InvalidReceiptError,
    OrderNotFoundError,
    PaymentNotFoundError,
)
from app.domain.repositories.order_repository import OrderRepository
from app.domain.repositories.payment_repository import PaymentRepository
from app.domain.storage import ReceiptStorage

MAX_RECEIPT_BYTES = 5 * 1024 * 1024  # 5 MB


def _detect_extension(content: bytes) -> Optional[str]:
    # Check the real file signature, not the name the user gave the file
    if content.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    return None


class SubmitPaymentProof:
    def __init__(self, payments: PaymentRepository, storage: ReceiptStorage):
        self.payments = payments
        self.storage = storage

    def execute(self, user_id: int, order_id: int, content: bytes) -> Payment:
        if not content:
            raise InvalidReceiptError("The uploaded file is empty")
        if len(content) > MAX_RECEIPT_BYTES:
            raise InvalidReceiptError("The receipt image must be 5 MB or smaller")
        extension = _detect_extension(content)
        if extension is None:
            raise InvalidReceiptError("Only JPG, JPEG or PNG images are allowed")

        stored_name = self.storage.save(content, extension)
        try:
            return self.payments.create_submission(order_id, user_id, stored_name)
        except Exception:
            # The database refused it, so don't leave an orphan file behind
            self.storage.delete(stored_name)
            raise


class GetMyPayment:
    def __init__(self, payments: PaymentRepository, orders: OrderRepository):
        self.payments = payments
        self.orders = orders

    def execute(self, user_id: int, order_id: int) -> Payment:
        order = self.orders.get_by_id(order_id)
        if order is None or order.user_id != user_id:
            raise OrderNotFoundError()
        payment = self.payments.get_latest_for_order(order_id)
        if payment is None:
            # Nothing uploaded yet
            return Payment(
                order_id=order_id,
                amount=Decimal(order.total_amount),
                status=PaymentStatus.NOT_SUBMITTED,
            )
        return payment


class AdminListPayments:
    def __init__(self, payments: PaymentRepository):
        self.payments = payments

    def execute(
        self, status: Optional[PaymentStatus], page: int, page_size: int
    ) -> Tuple[List[Payment], int]:
        return self.payments.list_all(status, page, page_size)


class AdminGetPayment:
    def __init__(self, payments: PaymentRepository):
        self.payments = payments

    def execute(self, payment_id: int) -> Payment:
        payment = self.payments.get_by_id(payment_id)
        if payment is None:
            raise PaymentNotFoundError()
        return payment


class GetReceiptFile:
    def __init__(self, payments: PaymentRepository, storage: ReceiptStorage):
        self.payments = payments
        self.storage = storage

    def execute(self, payment_id: int) -> Tuple[str, str]:
        payment = self.payments.get_by_id(payment_id)
        if payment is None:
            raise PaymentNotFoundError()
        media_type = "image/png" if payment.receipt_path.endswith(".png") else "image/jpeg"
        return self.storage.get_path(payment.receipt_path), media_type


class ApprovePayment:
    def __init__(self, payments: PaymentRepository):
        self.payments = payments

    def execute(self, admin_id: int, payment_id: int) -> Payment:
        return self.payments.review(payment_id, admin_id, approve=True, reason=None)


class RejectPayment:
    def __init__(self, payments: PaymentRepository):
        self.payments = payments

    def execute(self, admin_id: int, payment_id: int, reason: str) -> Payment:
        if not reason.strip():
            raise InvalidPaymentStateError("A rejection reason is required")
        return self.payments.review(
            payment_id, admin_id, approve=False, reason=reason.strip()
        )