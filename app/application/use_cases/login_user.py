from app.core.security import create_access_token, verify_password
from app.domain.exceptions import InvalidCredentialsError
from app.domain.repositories.user_repository import UserRepository


class LoginUser:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, email: str, password: str) -> str:
        user = self.repository.get_by_email(email.lower().strip())
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return create_access_token(user.id)