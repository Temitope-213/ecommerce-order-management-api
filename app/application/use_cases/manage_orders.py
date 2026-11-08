from typing import List, Optional, Tuple

from app.domain.entities.order import Order, OrderStatus
from app.domain.exceptions import OrderNotFoundError
from app.domain.repositories.order_repository import OrderRepository


class Checkout:
    def __init__(self, orders: OrderRepository):
        self.orders = orders

    def execute(self, user_id: int, idempotency_key: str) -> Tuple[Order, bool]:
        return self.orders.place_order(user_id, idempotency_key.strip())


class GetMyOrder:
    def __init__(self, orders: OrderRepository):
        self.orders = orders

    def execute(self, user_id: int, order_id: int) -> Order:
        order = self.orders.get_by_id(order_id)
        # Someone else's order looks exactly like a missing order (404)
        if order is None or order.user_id != user_id:
            raise OrderNotFoundError()
        return order


class ListMyOrders:
    def __init__(self, orders: OrderRepository):
        self.orders = orders

    def execute(self, user_id: int, page: int, page_size: int) -> Tuple[List[Order], int]:
        return self.orders.list_by_user(user_id, page, page_size)


class CancelMyOrder:
    def __init__(self, orders: OrderRepository):
        self.orders = orders

    def execute(self, user_id: int, order_id: int) -> Order:
        return self.orders.change_status(order_id, OrderStatus.CANCELLED, user_id=user_id)


class AdminListOrders:
    def __init__(self, orders: OrderRepository):
        self.orders = orders

    def execute(
        self, status: Optional[OrderStatus], page: int, page_size: int
    ) -> Tuple[List[Order], int]:
        return self.orders.list_all(status, page, page_size)


class AdminGetOrder:
    def __init__(self, orders: OrderRepository):
        self.orders = orders

    def execute(self, order_id: int) -> Order:
        order = self.orders.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError()
        return order


class UpdateOrderStatus:
    def __init__(self, orders: OrderRepository):
        self.orders = orders

    def execute(self, order_id: int, new_status: OrderStatus) -> Order:
        return self.orders.change_status(order_id, new_status)