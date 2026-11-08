from app.domain.entities.cart import Cart
from app.domain.exceptions import (
    CartItemNotFoundError,
    InsufficientStockError,
    ProductNotFoundError,
)
from app.domain.repositories.cart_repository import CartRepository
from app.domain.repositories.product_repository import ProductRepository


def _get_purchasable_product(products: ProductRepository, product_id: int):
    product = products.get_by_id(product_id)
    # Customers can only buy products that exist and are active
    if product is None or not product.is_active:
        raise ProductNotFoundError()
    return product


class AddToCart:
    def __init__(self, carts: CartRepository, products: ProductRepository):
        self.carts = carts
        self.products = products

    def execute(self, user_id: int, product_id: int, quantity: int) -> Cart:
        product = _get_purchasable_product(self.products, product_id)
        # Adding the same product again increases the existing quantity
        new_quantity = self.carts.get_item_quantity(user_id, product_id) + quantity
        if new_quantity > product.stock:
            raise InsufficientStockError(
                f"Only {product.stock} unit(s) of this product are available"
            )
        self.carts.set_item_quantity(user_id, product_id, new_quantity)
        return self.carts.get_cart(user_id)


class ViewCart:
    def __init__(self, carts: CartRepository):
        self.carts = carts

    def execute(self, user_id: int) -> Cart:
        return self.carts.get_cart(user_id)


class UpdateCartItem:
    def __init__(self, carts: CartRepository, products: ProductRepository):
        self.carts = carts
        self.products = products

    def execute(self, user_id: int, product_id: int, quantity: int) -> Cart:
        if self.carts.get_item_quantity(user_id, product_id) == 0:
            raise CartItemNotFoundError()
        product = _get_purchasable_product(self.products, product_id)
        if quantity > product.stock:
            raise InsufficientStockError(
                f"Only {product.stock} unit(s) of this product are available"
            )
        self.carts.set_item_quantity(user_id, product_id, quantity)
        return self.carts.get_cart(user_id)


class RemoveCartItem:
    def __init__(self, carts: CartRepository):
        self.carts = carts

    def execute(self, user_id: int, product_id: int) -> None:
        if not self.carts.remove_item(user_id, product_id):
            raise CartItemNotFoundError()


class ClearCart:
    def __init__(self, carts: CartRepository):
        self.carts = carts

    def execute(self, user_id: int) -> None:
        self.carts.clear(user_id)