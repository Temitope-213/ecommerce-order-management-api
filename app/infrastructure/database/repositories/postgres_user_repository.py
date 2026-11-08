from typing import Optional

import psycopg

from app.domain.entities.user import User
from app.domain.exceptions import EmailAlreadyExistsError
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.connection import get_connection


class PostgresUserRepository(UserRepository):
    def create(self, user: User) -> User:
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO users (username, email, password_hash, role)
                        VALUES (%s, %s, %s, %s)
                        RETURNING *
                        """,
                        (user.username, user.email, user.password_hash, user.role),
                    )
                    return User(**cur.fetchone())
        except psycopg.errors.UniqueViolation:
            raise EmailAlreadyExistsError()

    def get_by_email(self, email: str) -> Optional[User]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                row = cur.fetchone()
                return User(**row) if row else None

    def get_by_id(self, user_id: int) -> Optional[User]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
                return User(**row) if row else None