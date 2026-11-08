from app.domain.entities.cart import Cart, CartItem
from app.domain.repositories.cart_repository import CartRepository
from app.infrastructure.database.connection import get_connection


def _get_or_create_cart_id(cur, user_id: int) -> int:
    # Creates the customer's cart the first time it is needed
    cur.execute(
        "INSERT INTO carts (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
        (user_id,),
    )
    cur.execute("SELECT id FROM carts WHERE user_id = %s", (user_id,))
    return cur.fetchone()["id"]


class PostgresCartRepository(CartRepository):
    def get_cart(self, user_id: int) -> Cart:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT ci.product_id, p.name, p.price AS unit_price,
                           ci.quantity, p.stock, p.is_active
                    FROM cart_items ci
                    JOIN carts c ON c.id = ci.cart_id
                    JOIN products p ON p.id = ci.product_id
                    WHERE c.user_id = %s
                    ORDER BY ci.id
                    """,
                    (user_id,),
                )
                items = [CartItem(**row) for row in cur.fetchall()]
                return Cart(user_id=user_id, items=items)

    def get_item_quantity(self, user_id: int, product_id: int) -> int:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT ci.quantity
                    FROM cart_items ci
                    JOIN carts c ON c.id = ci.cart_id
                    WHERE c.user_id = %s AND ci.product_id = %s
                    """,
                    (user_id, product_id),
                )
                row = cur.fetchone()
                return row["quantity"] if row else 0

    def set_item_quantity(self, user_id: int, product_id: int, quantity: int) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cart_id = _get_or_create_cart_id(cur, user_id)
                cur.execute(
                    """
                    INSERT INTO cart_items (cart_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (cart_id, product_id)
                    DO UPDATE SET quantity = EXCLUDED.quantity
                    """,
                    (cart_id, product_id, quantity),
                )

    def remove_item(self, user_id: int, product_id: int) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM cart_items
                    WHERE product_id = %s
                      AND cart_id = (SELECT id FROM carts WHERE user_id = %s)
                    RETURNING id
                    """,
                    (product_id, user_id),
                )
                return cur.fetchone() is not None

    def clear(self, user_id: int) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM cart_items
                    WHERE cart_id = (SELECT id FROM carts WHERE user_id = %s)
                    """,
                    (user_id,),
                )