from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]: ...