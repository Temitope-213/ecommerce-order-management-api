from typing import List, Optional, Tuple

from app.domain.entities.payment import Payment, PaymentStatus
from app.domain.exceptions import (
    InvalidPaymentStateError,
    OrderNotFoundError,
    PaymentNotFoundError,
)
from app.domain.repositories.payment_repository import PaymentRepository
from app.infrastructure.database.connection import get_connection

_SELECT = """
    SELECT p.*, o.user_id AS user_id, o.status AS order_status
    FROM payments p
    JOIN orders o ON o.id = p.order_id
"""


def _to_payment(row) -> Payment:
    return Payment(
        id=row["id"],
        order_id=row["order_id"],
        amount=row["amount"],
        status=PaymentStatus(row["status"]),
        receipt_path=row["receipt_path"],
        rejection_reason=row["rejection_reason"],
        reviewed_by=row["reviewed_by"],
        reviewed_at=row["reviewed_at"],
        submitted_at=row["submitted_at"],
        user_id=row.get("user_id"),
        order_status=row.get("order_status"),
    )


class PostgresPaymentRepository(PaymentRepository):
    def create_submission(self, order_id: int, user_id: int, receipt_path: str) -> Payment:
        with get_connection() as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    # Lock the order so uploads and cancellations can't clash
                    cur.execute(
                        "SELECT * FROM orders WHERE id = %s FOR UPDATE", (order_id,)
                    )
                    order = cur.fetchone()
                    if order is None or order["user_id"] != user_id:
                        raise OrderNotFoundError()
                    if order["status"] != "PENDING":
                        raise InvalidPaymentStateError(
                            "Payment proof can only be submitted for a PENDING order"
                        )

                    cur.execute(
                        """
                        SELECT status FROM payments
                        WHERE order_id = %s ORDER BY id DESC LIMIT 1
                        """,
                        (order_id,),
                    )
                    latest = cur.fetchone()
                    if latest and latest["status"] == "UNDER_REVIEW":
                        raise InvalidPaymentStateError(
                            "Your payment proof is already under review"
                        )
                    if latest and latest["status"] == "APPROVED":
                        raise InvalidPaymentStateError(
                            "This order's payment has already been approved"
                        )

                    # The amount comes from the order, never from the client
                    cur.execute(
                        """
                        INSERT INTO payments (order_id, amount, status, receipt_path)
                        VALUES (%s, %s, 'UNDER_REVIEW', %s)
                        RETURNING *
                        """,
                        (order_id, order["total_amount"], receipt_path),
                    )
                    row = cur.fetchone()
                    row["user_id"] = order["user_id"]
                    row["order_status"] = order["status"]
                    return _to_payment(row)

    def get_latest_for_order(self, order_id: int) -> Optional[Payment]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    _SELECT + " WHERE p.order_id = %s ORDER BY p.id DESC LIMIT 1",
                    (order_id,),
                )
                row = cur.fetchone()
                return _to_payment(row) if row else None

    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(_SELECT + " WHERE p.id = %s", (payment_id,))
                row = cur.fetchone()
                return _to_payment(row) if row else None

    def list_all(
        self, status: Optional[PaymentStatus], page: int, page_size: int
    ) -> Tuple[List[Payment], int]:
        offset = (page - 1) * page_size
        where = "WHERE p.status = %s" if status else ""
        params = [status.value] if status else []
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT COUNT(*) AS total FROM payments p {where}", params
                )
                total = cur.fetchone()["total"]
                cur.execute(
                    f"{_SELECT} {where} ORDER BY p.submitted_at DESC, p.id DESC "
                    "LIMIT %s OFFSET %s",
                    params + [page_size, offset],
                )
                return [_to_payment(r) for r in cur.fetchall()], total

    def review(
        self, payment_id: int, admin_id: int, approve: bool, reason: Optional[str]
    ) -> Payment:
        with get_connection() as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT order_id FROM payments WHERE id = %s", (payment_id,)
                    )
                    found = cur.fetchone()
                    if found is None:
                        raise PaymentNotFoundError()

                    # Same lock order everywhere: order first, then payment
                    cur.execute(
                        "SELECT status FROM orders WHERE id = %s FOR UPDATE",
                        (found["order_id"],),
                    )
                    order = cur.fetchone()
                    cur.execute(
                        "SELECT * FROM payments WHERE id = %s FOR UPDATE", (payment_id,)
                    )
                    payment = cur.fetchone()

                    if payment["status"] != "UNDER_REVIEW":
                        raise InvalidPaymentStateError(
                            "Only a payment that is UNDER_REVIEW can be reviewed"
                        )
                    if approve and order["status"] != "PENDING":
                        raise InvalidPaymentStateError(
                            "This order is no longer pending, so it cannot be confirmed"
                        )

                    cur.execute(
                        """
                        UPDATE payments
                        SET status = %s, rejection_reason = %s,
                            reviewed_by = %s, reviewed_at = NOW()
                        WHERE id = %s
                        """,
                        (
                            "APPROVED" if approve else "REJECTED",
                            None if approve else reason,
                            admin_id,
                            payment_id,
                        ),
                    )
                    if approve:
                        cur.execute(
                            """
                            UPDATE orders SET status = 'CONFIRMED', updated_at = NOW()
                            WHERE id = %s
                            """,
                            (found["order_id"],),
                        )

                    cur.execute(_SELECT + " WHERE p.id = %s", (payment_id,))
                    return _to_payment(cur.fetchone())

    def has_approved_payment(self, order_id: int) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1 FROM payments
                    WHERE order_id = %s AND status = 'APPROVED' LIMIT 1
                    """,
                    (order_id,),
                )
                return cur.fetchone() is not None