import getpass

from app.core.security import hash_password
from app.domain.entities.user import User
from app.domain.exceptions import EmailAlreadyExistsError
from app.infrastructure.database.repositories.postgres_user_repository import (
    PostgresUserRepository,
)


def main():
    print("Create an administrator account")
    username = input("Username: ").strip()
    email = input("Email: ").strip().lower()
    password = getpass.getpass("Password (at least 8 characters): ")

    if len(username) < 3 or "@" not in email or len(password) < 8:
        print("Invalid input. Nothing was created.")
        return

    repo = PostgresUserRepository()
    try:
        repo.create(
            User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                role="admin",
            )
        )
    except EmailAlreadyExistsError:
        print("That email is already registered.")
        return
    print("Administrator created.")


if __name__ == "__main__":
    main()