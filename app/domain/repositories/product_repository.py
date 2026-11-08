from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Tuple

from app.domain.entities.product import Product


@dataclass
class ProductFilters:
    search: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    sort_by: str = "created_at"   # "price" or "created_at"
    order: str = "desc"           # "asc" or "desc"
    page: int = 1
    page_size: int = 10
    include_inactive: bool = False  # admins only


class ProductRepository(ABC):
    @abstractmethod
    def create(self, product: Product) -> Product: ...

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]: ...

    @abstractmethod
    def list(self, filters: ProductFilters) -> Tuple[List[Product], int]:
        """Returns (products on this page, total matching products)."""

    @abstractmethod
    def update(self, product_id: int, product: Product) -> Optional[Product]: ...

    @abstractmethod
    def update_stock(self, product_id: int, stock: int) -> Optional[Product]: ...

    @abstractmethod
    def deactivate(self, product_id: int) -> bool: ...