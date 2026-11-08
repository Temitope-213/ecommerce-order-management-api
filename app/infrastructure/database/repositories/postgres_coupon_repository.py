from typing import List, Optional, Tuple

import psycopg

from app.domain.entities.coupon import Coupon
from app.domain.exceptions import CouponAlreadyExistsError
from app.domain.repositories.coupon_repository import CouponRepository
from app.infrastructure.database.connection import get_connection

# times_used is counted from coupon_usage, so it can never drift out of sync
_SELECT = """
    SELECT c.*,
           (SELECT COUNT(*) FROM coupon_usage u WHERE u.coupon_id = c.id) AS times_used
    FROM coupons c
"""


class PostgresCouponRepository(CouponRepository):
    def create(self, coupon: Coupon) -> Coupon:
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO coupons
                            (code, discount_type, discount_value, expires_at,
                             max_uses, min_order_amount, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            coupon.code, coupon.discount_type, coupon.discount_value,
                            coupon.expires_at, coupon.max_uses,
                            coupon.min_order_amount, coupon.is_active,
                        ),
                    )
                    new_id = cur.fetchone()["id"]
                    cur.execute(_SELECT + " WHERE c.id = %s", (new_id,))
                    return Coupon(**cur.fetchone())
        except psycopg.errors.UniqueViolation:
            raise CouponAlreadyExistsError()

    def get_by_id(self, coupon_id: int) -> Optional[Coupon]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(_SELECT + " WHERE c.id = %s", (coupon_id,))
                row = cur.fetchone()
                return Coupon(**row) if row else None

    def list_all(self, page: int, page_size: int) -> Tuple[List[Coupon], int]:
        offset = (page - 1) * page_size
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS total FROM coupons")
                total = cur.fetchone()["total"]
                cur.execute(
                    _SELECT + " ORDER BY c.created_at DESC, c.id DESC LIMIT %s OFFSET %s",
                    (page_size, offset),
                )
                return [Coupon(**r) for r in cur.fetchall()], total

    def update(self, coupon_id: int, coupon: Coupon) -> Optional[Coupon]:
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE coupons
                        SET code = %s, discount_type = %s, discount_value = %s,
                            expires_at = %s, max_uses = %s, min_order_amount = %s,
                            is_active = %s
                        WHERE id = %s
                        RETURNING id
                        """,
                        (
                            coupon.code, coupon.discount_type, coupon.discount_value,
                            coupon.expires_at, coupon.max_uses,
                            coupon.min_order_amount, coupon.is_active, coupon_id,
                        ),
                    )
                    if cur.fetchone() is None:
                        return None
                    cur.execute(_SELECT + " WHERE c.id = %s", (coupon_id,))
                    return Coupon(**cur.fetchone())
        except psycopg.errors.UniqueViolation:
            raise CouponAlreadyExistsError()

    def deactivate(self, coupon_id: int) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE coupons SET is_active = FALSE WHERE id = %s RETURNING id",
                    (coupon_id,),
                )
                return cur.fetchone() is not None