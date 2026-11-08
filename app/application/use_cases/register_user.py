from app.core.security import hash_password
from app.domain.entities.user import User
from app.domain.exceptions import EmailAlreadyExistsError
from app.domain.repositories.user_repository import UserRepository


class RegisterUser:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, username: str, email: str, password: str) -> User:
        email = email.lower().strip()
        if self.repository.get_by_email(email) is not None:
            raise EmailAlreadyExistsError()
        user = User(
            username=username.strip(),
            email=email,
            password_hash=hash_password(password),  # scramble before saving
        )
        return self.repository.create(user)