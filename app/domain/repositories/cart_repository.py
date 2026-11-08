from abc import ABC, abstractmethod

from app.domain.entities.cart import Cart


class CartRepository(ABC):
    @abstractmethod
    def get_cart(self, user_id: int) -> Cart: ...

    @abstractmethod
    def get_item_quantity(self, user_id: int, product_id: int) -> int:
        """Returns the quantity of this product in the user's cart, or 0."""

    @abstractmethod
    def set_item_quantity(self, user_id: int, product_id: int, quantity: int) -> None:
        """Adds the item, or replaces its quantity if it is already in the cart."""

    @abstractmethod
    def remove_item(self, user_id: int, product_id: int) -> bool: ...

    @abstractmethod
    def clear(self, user_id: int) -> None: ...