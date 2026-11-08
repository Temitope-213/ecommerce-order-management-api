class EmailAlreadyExistsError(Exception):
    """Raised when an email is already registered."""


class InvalidCredentialsError(Exception):
    """Raised when the email or password is wrong."""


class CategoryNotFoundError(Exception):
    """Raised when a category does not exist."""


class CategoryAlreadyExistsError(Exception):
    """Raised when a category name is already taken."""


class ProductNotFoundError(Exception):
    """Raised when a product does not exist."""


class SkuAlreadyExistsError(Exception):
    """Raised when a product SKU is already used."""


class InvalidProductError(ValueError):
    """Raised when product data breaks a business rule."""


class CartItemNotFoundError(Exception):
    """Raised when a product is not in the customer's cart."""


class InsufficientStockError(Exception):
    """Raised when stock is too low or a product is unavailable."""


class EmptyCartError(Exception):
    """Raised when checkout is attempted with an empty cart."""


class OrderNotFoundError(Exception):
    """Raised when an order does not exist or belongs to someone else."""


class InvalidStatusTransitionError(Exception):
    """Raised when an order status change is not allowed."""


class PaymentNotFoundError(Exception):
    """Raised when a payment does not exist."""


class InvalidPaymentStateError(Exception):
    """Raised when a payment action is not allowed in the current state."""


class InvalidReceiptError(Exception):
    """Raised when the uploaded receipt is not a valid image."""


class PaymentRequiredError(Exception):
    """Raised when an order needs an approved payment first."""