import logging

import psycopg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import (
    admin,
    admin_orders,
    auth,
    cart,
    categories,
    orders,
    payments,
    products,
)
from app.domain.exceptions import (
    CartItemNotFoundError,
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    EmailAlreadyExistsError,
    EmptyCartError,
    InsufficientStockError,
    InvalidCredentialsError,
    InvalidPaymentStateError,
    InvalidProductError,
    InvalidReceiptError,
    InvalidStatusTransitionError,
    OrderNotFoundError,
    PaymentNotFoundError,
    PaymentRequiredError,
    ProductNotFoundError,
    SkuAlreadyExistsError,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="E-Commerce & Order Management API")
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(admin_orders.router)
app.include_router(payments.router)
app.include_router(payments.admin_router)


def _error(status_code: int, message: str, headers=None):
    return JSONResponse(status_code=status_code, content={"detail": message}, headers=headers)


@app.exception_handler(EmailAlreadyExistsError)
async def email_exists(request: Request, exc: EmailAlreadyExistsError):
    return _error(409, "Email is already registered")


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials(request: Request, exc: InvalidCredentialsError):
    return _error(401, "Incorrect email or password", {"WWW-Authenticate": "Bearer"})


@app.exception_handler(CategoryNotFoundError)
async def category_not_found(request: Request, exc: CategoryNotFoundError):
    return _error(404, "Category not found")


@app.exception_handler(CategoryAlreadyExistsError)
async def category_exists(request: Request, exc: CategoryAlreadyExistsError):
    return _error(409, "A category with this name already exists")


@app.exception_handler(ProductNotFoundError)
async def product_not_found(request: Request, exc: ProductNotFoundError):
    return _error(404, "Product not found")


@app.exception_handler(SkuAlreadyExistsError)
async def sku_exists(request: Request, exc: SkuAlreadyExistsError):
    return _error(409, "A product with this SKU already exists")


@app.exception_handler(InvalidProductError)
async def invalid_product(request: Request, exc: InvalidProductError):
    return _error(422, str(exc))


@app.exception_handler(CartItemNotFoundError)
async def cart_item_not_found(request: Request, exc: CartItemNotFoundError):
    return _error(404, "This product is not in your cart")


@app.exception_handler(InsufficientStockError)
async def insufficient_stock(request: Request, exc: InsufficientStockError):
    return _error(409, str(exc) or "Not enough stock available")


@app.exception_handler(EmptyCartError)
async def empty_cart(request: Request, exc: EmptyCartError):
    return _error(400, "Your cart is empty")


@app.exception_handler(OrderNotFoundError)
async def order_not_found(request: Request, exc: OrderNotFoundError):
    return _error(404, "Order not found")


@app.exception_handler(InvalidStatusTransitionError)
async def invalid_status_transition(request: Request, exc: InvalidStatusTransitionError):
    return _error(409, str(exc))


@app.exception_handler(PaymentNotFoundError)
async def payment_not_found(request: Request, exc: PaymentNotFoundError):
    return _error(404, "Payment not found")


@app.exception_handler(InvalidPaymentStateError)
async def invalid_payment_state(request: Request, exc: InvalidPaymentStateError):
    return _error(409, str(exc))


@app.exception_handler(InvalidReceiptError)
async def invalid_receipt(request: Request, exc: InvalidReceiptError):
    return _error(422, str(exc))


@app.exception_handler(PaymentRequiredError)
async def payment_required(request: Request, exc: PaymentRequiredError):
    return _error(409, "The order needs an approved payment before this status change")


@app.exception_handler(psycopg.OperationalError)
async def db_connection_error(request: Request, exc: psycopg.OperationalError):
    logger.error("Database connection error")
    return _error(503, "Database unavailable")


@app.exception_handler(psycopg.Error)
async def db_error(request: Request, exc: psycopg.Error):
    logger.error("Database error: %s", type(exc).__name__)
    return _error(500, "Internal server error")