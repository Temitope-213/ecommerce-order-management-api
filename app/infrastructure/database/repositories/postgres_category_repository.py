from typing import List, Optional

import psycopg

from app.domain.entities.category import Category
from app.domain.exceptions import CategoryAlreadyExistsError
from app.domain.repositories.category_repository import CategoryRepository
from app.infrastructure.database.connection import get_connection


class PostgresCategoryRepository(CategoryRepository):
    def create(self, category: Category) -> Category:
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO categories (name, description)
                        VALUES (%s, %s)
                        RETURNING *
                        """,
                        (category.name, category.description),
                    )
                    return Category(**cur.fetchone())
        except psycopg.errors.UniqueViolation:
            raise CategoryAlreadyExistsError()

    def get_all(self) -> List[Category]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM categories ORDER BY name")
                return [Category(**row) for row in cur.fetchall()]

    def update(self, category_id: int, category: Category) -> Optional[Category]:
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE categories SET name = %s, description = %s
                        WHERE id = %s
                        RETURNING *
                        """,
                        (category.name, category.description, category_id),
                    )
                    row = cur.fetchone()
                    return Category(**row) if row else None
        except psycopg.errors.UniqueViolation:
            raise CategoryAlreadyExistsError()

    def delete(self, category_id: int) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM categories WHERE id = %s RETURNING id",
                    (category_id,),
                )
                return cur.fetchone() is not None


    def get_by_id(self, category_id: int) -> Optional[Category]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM categories WHERE id = %s",
                    (category_id,),
                )
                row = cur.fetchone()
                return Category(**row) if row else None