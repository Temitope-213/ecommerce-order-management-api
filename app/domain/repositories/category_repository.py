from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.category import Category


class CategoryRepository(ABC):
    @abstractmethod
    def create(self, category: Category) -> Category: ...

    @abstractmethod
    def get_all(self) -> List[Category]: ...

    @abstractmethod
    def update(self, category_id: int, category: Category) -> Optional[Category]: ...

    @abstractmethod
    def delete(self, category_id: int) -> bool: ...