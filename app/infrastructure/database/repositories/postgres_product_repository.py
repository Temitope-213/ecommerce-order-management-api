from typing import List, Optional, Tuple

import psycopg

from app.domain.entities.product import Product
from app.domain.exceptions import SkuAlreadyExistsError
from app.domain.repositories.product_repository import (
    ProductFilters,
    ProductRepository,
)
from app.infrastructure.database.connection import get_connection

# Whitelists: user input is never pasted into SQL directly
SORT_COLUMNS = {"price": "price", "created_at": "created_at"}
SORT_ORDERS = {"asc": "ASC", "desc": "DESC"}


class PostgresProductRepository(ProductRepository):
    def create(self, product: Product) -> Product:
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO products
                            (name, description, price, stock, category_id, sku, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING *
                        """,
                        (
                            product.name, product.description, product.price,
                            product.stock, product.category_id, product.sku,
                            product.is_active,
                        ),
                    )
                    return Product(**cur.fetchone())
        except psycopg.errors.UniqueViolation:
            raise SkuAlreadyExistsError()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
                row = cur.fetchone()
                return Product(**row) if row else None

    def list(self, filters: ProductFilters) -> Tuple[List[Product], int]:
        conditions = []
        params = []

        if not filters.include_inactive:
            conditions.append("is_active = TRUE")
        if filters.search:
            conditions.append("name ILIKE %s")
            params.append(f"%{filters.search}%")
        if filters.category_id is not None:
            conditions.append("category_id = %s")
            params.append(filters.category_id)
        if filters.min_price is not None:
            conditions.append("price >= %s")
            params.append(filters.min_price)
        if filters.max_price is not None:
            conditions.append("price <= %s")
            params.append(filters.max_price)

        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        sort_column = SORT_COLUMNS[filters.sort_by]
        direction = SORT_ORDERS[filters.order]
        offset = (filters.page - 1) * filters.page_size

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) AS total FROM products {where}", params)
                total = cur.fetchone()["total"]
                cur.execute(
                    f"""
                    SELECT * FROM products {where}
                    ORDER BY {sort_column} {direction}, id
                    LIMIT %s OFFSET %s
                    """,
                    params + [filters.page_size, offset],
                )
                return [Product(**row) for row in cur.fetchall()], total

    def update(self, product_id: int, product: Product) -> Optional[Product]:
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE products
                        SET name = %s, description = %s, price = %s,
                            category_id = %s, sku = %s
                        WHERE id = %s
                        RETURNING *
                        """,
                        (
                            product.name, product.description, product.price,
                            product.category_id, product.sku, product_id,
                        ),
                    )
                    row = cur.fetchone()
                    return Product(**row) if row else None
        except psycopg.errors.UniqueViolation:
            raise SkuAlreadyExistsError()

    def update_stock(self, product_id: int, stock: int) -> Optional[Product]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE products SET stock = %s WHERE id = %s RETURNING *",
                    (stock, product_id),
                )
                row = cur.fetchone()
                return Product(**row) if row else None

    def deactivate(self, product_id: int) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE products SET is_active = FALSE WHERE id = %s RETURNING id",
                    (product_id,),
                )
                return cur.fetchone() is not None