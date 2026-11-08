from decimal import Decimal
from typing import List, Optional, Tuple

from app.domain.entities.product import Product
from app.domain.exceptions import (
    CategoryNotFoundError,
    InvalidProductError,
    ProductNotFoundError,
)
from app.domain.repositories.category_repository import CategoryRepository
from app.domain.repositories.product_repository import (
    ProductFilters,
    ProductRepository,
)

MAX_PAGE_SIZE = 100


def _validate(name: str, price: Decimal, sku: str) -> None:
    if not name.strip():
        raise InvalidProductError("Product name cannot be empty")
    if not sku.strip():
        raise InvalidProductError("SKU cannot be empty")
    if price < 0:
        raise InvalidProductError("Price cannot be negative")


class CreateProduct:
    def __init__(self, products: ProductRepository, categories: CategoryRepository):
        self.products = products
        self.categories = categories

    def execute(
        self, name: str, price: Decimal, sku: str, stock: int,
        description: Optional[str], category_id: Optional[int],
    ) -> Product:
        _validate(name, price, sku)
        if stock < 0:
            raise InvalidProductError("Stock cannot be negative")
        if category_id is not None and self.categories.get_by_id(category_id) is None:
            raise CategoryNotFoundError()
        return self.products.create(
            Product(
                name=name.strip(), price=price, sku=sku.strip(),
                stock=stock, description=description, category_id=category_id,
            )
        )


class GetProduct:
    def __init__(self, products: ProductRepository):
        self.products = products

    def execute(self, product_id: int, is_admin: bool = False) -> Product:
        product = self.products.get_by_id(product_id)
        # Customers must not see inactive products
        if product is None or (not product.is_active and not is_admin):
            raise ProductNotFoundError()
        return product


class ListProducts:
    def __init__(self, products: ProductRepository):
        self.products = products

    def execute(self, filters: ProductFilters) -> Tuple[List[Product], int]:
        if filters.sort_by not in ("price", "created_at"):
            raise InvalidProductError("sort_by must be 'price' or 'created_at'")
        if filters.order not in ("asc", "desc"):
            raise InvalidProductError("order must be 'asc' or 'desc'")
        if filters.min_price is not None and filters.max_price is not None \
                and filters.min_price > filters.max_price:
            raise InvalidProductError("min_price cannot be greater than max_price")
        filters.page = max(filters.page, 1)
        filters.page_size = min(max(filters.page_size, 1), MAX_PAGE_SIZE)
        return self.products.list(filters)


class UpdateProduct:
    def __init__(self, products: ProductRepository, categories: CategoryRepository):
        self.products = products
        self.categories = categories

    def execute(
        self, product_id: int, name: str, price: Decimal, sku: str,
        description: Optional[str], category_id: Optional[int],
    ) -> Product:
        _validate(name, price, sku)
        if category_id is not None and self.categories.get_by_id(category_id) is None:
            raise CategoryNotFoundError()
        updated = self.products.update(
            product_id,
            Product(
                name=name.strip(), price=price, sku=sku.strip(),
                description=description, category_id=category_id,
            ),
        )
        if updated is None:
            raise ProductNotFoundError()
        return updated


class UpdateStock:
    def __init__(self, products: ProductRepository):
        self.products = products

    def execute(self, product_id: int, stock: int) -> Product:
        if stock < 0:
            raise InvalidProductError("Stock cannot be negative")
        updated = self.products.update_stock(product_id, stock)
        if updated is None:
            raise ProductNotFoundError()
        return updated


class DeactivateProduct:
    def __init__(self, products: ProductRepository):
        self.products = products

    def execute(self, product_id: int) -> None:
        if not self.products.deactivate(product_id):
            raise ProductNotFoundError()