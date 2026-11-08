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