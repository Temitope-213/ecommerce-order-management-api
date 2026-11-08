from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.domain.entities.order import Order, OrderStatus


class OrderRepository(ABC):
    @abstractmethod
    def place_order(
        self, user_id: int, idempotency_key: str, coupon_code: Optional[str] = None
    ) -> Tuple[Order, bool]:
        """Turns the user's cart into an order in ONE transaction.
        Returns (order, created). created is False when the same
        idempotency key was already used (the original order is returned)."""

    @abstractmethod
    def get_by_id(self, order_id: int) -> Optional[Order]: ...

    @abstractmethod
    def list_by_user(
        self, user_id: int, page: int, page_size: int
    ) -> Tuple[List[Order], int]: ...

    @abstractmethod
    def list_all(
        self, status: Optional[OrderStatus], page: int, page_size: int
    ) -> Tuple[List[Order], int]: ...

    @abstractmethod
    def change_status(
        self, order_id: int, new_status: OrderStatus, user_id: Optional[int] = None
    ) -> Order:
        """Changes the status in one transaction (restocks on cancel).
        If user_id is given, the order must belong to that user."""