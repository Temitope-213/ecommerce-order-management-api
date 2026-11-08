from typing import List, Optional, Tuple

from app.domain.entities.order import (
    Order,
    OrderItem,
    OrderStatus,
    ensure_transition,
)
from app.domain.exceptions import (
    EmptyCartError,
    InsufficientStockError,
    OrderNotFoundError,
)
from app.domain.repositories.order_repository import OrderRepository
from app.infrastructure.database.connection import get_connection


def _to_order(row, items: List[OrderItem]) -> Order:
    return Order(
        id=row["id"],
        user_id=row["user_id"],
        status=OrderStatus(row["status"]),
        subtotal=row["subtotal"],
        discount_amount=row["discount_amount"],
        total_amount=row["total_amount"],
        coupon_id=row["coupon_id"],
        idempotency_key=row["idempotency_key"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        items=items,
    )


def _build_orders(cur, rows) -> List[Order]:
    """Attaches the items to each order row using ONE query."""
    if not rows:
        return []
    cur.execute(
        """
        SELECT id, order_id, product_id, product_name, unit_price, quantity
        FROM order_items
        WHERE order_id = ANY(%s)
        ORDER BY id
        """,
        ([r["id"] for r in rows],),
    )
    grouped = {}
    for item in cur.fetchall():
        grouped.setdefault(item["order_id"], []).append(
            OrderItem(
                id=item["id"],
                product_id=item["product_id"],
                product_name=item["product_name"],
                unit_price=item["unit_price"],
                quantity=item["quantity"],
            )
        )
    return [_to_order(r, grouped.get(r["id"], [])) for r in rows]


class PostgresOrderRepository(OrderRepository):
    def place_order(self, user_id: int, idempotency_key: str) -> Tuple[Order, bool]:
        with get_connection() as conn:
            # Everything inside this block is ONE transaction.
            # Any exception rolls back ALL of it (order, items, stock, cart).
            with conn.transaction():
                with conn.cursor() as cur:
                    # 1. Lock this customer's cart so their checkouts run one at a time
                    cur.execute(
                        "SELECT id FROM carts WHERE user_id = %s FOR UPDATE",
                        (user_id,),
                    )
                    cart = cur.fetchone()

                    # 2. Idempotency: same key as before? Return the original order
                    cur.execute(
                        "SELECT * FROM orders WHERE user_id = %s AND idempotency_key = %s",
                        (user_id, idempotency_key),
                    )
                    existing = cur.fetchone()
                    if existing:
                        return _build_orders(cur, [existing])[0], False

                    # 3. Read the cart
                    if cart is None:
                        raise EmptyCartError()
                    cur.execute(
                        """
                        SELECT product_id, quantity FROM cart_items
                        WHERE cart_id = %s ORDER BY product_id
                        """,
                        (cart["id"],),
                    )
                    cart_items = cur.fetchall()
                    if not cart_items:
                        raise EmptyCartError()

                    # 4. Deduct stock with ONE atomic conditional UPDATE per product.
                    #    The price is read from the database, never from the client.
                    #    Sorted by product_id so two checkouts never deadlock.
                    lines = []
                    for ci in cart_items:
                        cur.execute(
                            """
                            UPDATE products
                            SET stock = stock - %s
                            WHERE id = %s AND is_active = TRUE AND stock >= %s
                            RETURNING id, name, price
                            """,
                            (ci["quantity"], ci["product_id"], ci["quantity"]),
                        )
                        product = cur.fetchone()
                        if product is None:
                            cur.execute(
                                "SELECT name FROM products WHERE id = %s",
                                (ci["product_id"],),
                            )
                            found = cur.fetchone()
                            label = found["name"] if found else f"#{ci['product_id']}"
                            raise InsufficientStockError(
                                f"'{label}' is unavailable or has less than "
                                f"{ci['quantity']} unit(s) in stock"
                            )
                        lines.append((product, ci["quantity"]))

                    subtotal = sum(p["price"] * qty for p, qty in lines)

                    # 5. Create the order
                    cur.execute(
                        """
                        INSERT INTO orders
                            (user_id, status, subtotal, discount_amount,
                             total_amount, idempotency_key)
                        VALUES (%s, 'PENDING', %s, 0, %s, %s)
                        RETURNING *
                        """,
                        (user_id, subtotal, subtotal, idempotency_key),
                    )
                    order_row = cur.fetchone()

                    # 6. Snapshot name and price into the order items
                    for product, qty in lines:
                        cur.execute(
                            """
                            INSERT INTO order_items
                                (order_id, product_id, product_name, unit_price, quantity)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (order_row["id"], product["id"], product["name"],
                             product["price"], qty),
                        )

                    # 7. Empty the cart
                    cur.execute("DELETE FROM cart_items WHERE cart_id = %s", (cart["id"],))

                    return _build_orders(cur, [order_row])[0], True

    def get_by_id(self, order_id: int) -> Optional[Order]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
                row = cur.fetchone()
                return _build_orders(cur, [row])[0] if row else None

    def list_by_user(
        self, user_id: int, page: int, page_size: int
    ) -> Tuple[List[Order], int]:
        offset = (page - 1) * page_size
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) AS total FROM orders WHERE user_id = %s",
                    (user_id,),
                )
                total = cur.fetchone()["total"]
                cur.execute(
                    """
                    SELECT * FROM orders WHERE user_id = %s
                    ORDER BY created_at DESC, id DESC
                    LIMIT %s OFFSET %s
                    """,
                    (user_id, page_size, offset),
                )
                return _build_orders(cur, cur.fetchall()), total

    def list_all(
        self, status: Optional[OrderStatus], page: int, page_size: int
    ) -> Tuple[List[Order], int]:
        offset = (page - 1) * page_size
        where = "WHERE status = %s" if status else ""
        params = [status.value] if status else []
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) AS total FROM orders {where}", params)
                total = cur.fetchone()["total"]
                cur.execute(
                    f"""
                    SELECT * FROM orders {where}
                    ORDER BY created_at DESC, id DESC
                    LIMIT %s OFFSET %s
                    """,
                    params + [page_size, offset],
                )
                return _build_orders(cur, cur.fetchall()), total

    def change_status(
        self, order_id: int, new_status: OrderStatus, user_id: Optional[int] = None
    ) -> Order:
        with get_connection() as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    # Lock the order row so two requests can't cancel it twice
                    cur.execute(
                        "SELECT * FROM orders WHERE id = %s FOR UPDATE", (order_id,)
                    )
                    row = cur.fetchone()
                    if row is None or (user_id is not None and row["user_id"] != user_id):
                        raise OrderNotFoundError()

                    ensure_transition(OrderStatus(row["status"]), new_status)

                    # Cancelling returns the stock
                    if new_status == OrderStatus.CANCELLED:
                        cur.execute(
                            """
                            SELECT product_id, quantity FROM order_items
                            WHERE order_id = %s AND product_id IS NOT NULL
                            ORDER BY product_id
                            """,
                            (order_id,),
                        )
                        for item in cur.fetchall():
                            cur.execute(
                                "UPDATE products SET stock = stock + %s WHERE id = %s",
                                (item["quantity"], item["product_id"]),
                            )

                    cur.execute(
                        """
                        UPDATE orders SET status = %s, updated_at = NOW()
                        WHERE id = %s RETURNING *
                        """,
                        (new_status.value, order_id),
                    )
                    updated = cur.fetchone()
                    return _build_orders(cur, [updated])[0]