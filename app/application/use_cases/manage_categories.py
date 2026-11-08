from typing import List, Optional

from app.domain.entities.category import Category
from app.domain.exceptions import CategoryNotFoundError
from app.domain.repositories.category_repository import CategoryRepository


class CreateCategory:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self, name: str, description: Optional[str]) -> Category:
        return self.repository.create(Category(name=name.strip(), description=description))


class ListCategories:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self) -> List[Category]:
        return self.repository.get_all()


class UpdateCategory:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self, category_id: int, name: str, description: Optional[str]) -> Category:
        updated = self.repository.update(
            category_id, Category(name=name.strip(), description=description)
        )
        if updated is None:
            raise CategoryNotFoundError()
        return updated


class DeleteCategory:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self, category_id: int) -> None:
        if not self.repository.delete(category_id):
            raise CategoryNotFoundError()