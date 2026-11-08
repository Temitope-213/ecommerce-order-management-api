from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.use_cases.login_user import LoginUser
from app.application.use_cases.manage_cart import (
    AddToCart,
    ClearCart,
    RemoveCartItem,
    UpdateCartItem,
    ViewCart,
)
from app.application.use_cases.manage_categories import (
    CreateCategory,
    DeleteCategory,
    ListCategories,
    UpdateCategory,
)
from app.application.use_cases.manage_coupons import (
    CreateCoupon,
    DeactivateCoupon,
    GetCoupon,
    ListCoupons,
    UpdateCoupon,
)
from app.application.use_cases.manage_orders import (
    AdminGetOrder,
    AdminListOrders,
    CancelMyOrder,
    Checkout,
    GetMyOrder,
    ListMyOrders,
    UpdateOrderStatus,
)
from app.application.use_cases.manage_payments import (
    AdminGetPayment,
    AdminListPayments,
    ApprovePayment,
    GetMyPayment,
    GetReceiptFile,
    RejectPayment,
    SubmitPaymentProof,
)
from app.application.use_cases.manage_products import (
    CreateProduct,
    DeactivateProduct,
    GetProduct,
    ListProducts,
    UpdateProduct,
    UpdateStock,
)
from app.application.use_cases.register_user import RegisterUser
from app.core.security import decode_access_token
from app.domain.entities.user import User
from app.domain.repositories.cart_repository import CartRepository
from app.domain.repositories.category_repository import CategoryRepository
from app.domain.repositories.coupon_repository import CouponRepository
from app.domain.repositories.order_repository import OrderRepository
from app.domain.repositories.payment_repository import PaymentRepository
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.storage import ReceiptStorage
from app.infrastructure.database.repositories.postgres_cart_repository import (
    PostgresCartRepository,
)
from app.infrastructure.database.repositories.postgres_category_repository import (
    PostgresCategoryRepository,
)
from app.infrastructure.database.repositories.postgres_coupon_repository import (
    PostgresCouponRepository,
)
from app.infrastructure.database.repositories.postgres_order_repository import (
    PostgresOrderRepository,
)
from app.infrastructure.database.repositories.postgres_payment_repository import (
    PostgresPaymentRepository,
)
from app.infrastructure.database.repositories.postgres_product_repository import (
    PostgresProductRepository,
)
from app.infrastructure.database.repositories.postgres_user_repository import (
    PostgresUserRepository,
)
from app.infrastructure.storage.local_receipt_storage import LocalReceiptStorage

# Reads the "Authorization: Bearer <token>" header
bearer_scheme = HTTPBearer(auto_error=False)


# ---------- Repositories and storage (the only place that picks the implementation) ----------
def get_user_repository() -> UserRepository:
    return PostgresUserRepository()


def get_category_repository() -> CategoryRepository:
    return PostgresCategoryRepository()


def get_product_repository() -> ProductRepository:
    return PostgresProductRepository()


def get_cart_repository() -> CartRepository:
    return PostgresCartRepository()


def get_order_repository() -> OrderRepository:
    return PostgresOrderRepository()


def get_payment_repository() -> PaymentRepository:
    return PostgresPaymentRepository()


def get_coupon_repository() -> CouponRepository:
    return PostgresCouponRepository()


def get_receipt_storage() -> ReceiptStorage:
    return LocalReceiptStorage()


# ---------- Use cases ----------
def register_user_use_case(repo: UserRepository = Depends(get_user_repository)):
    return RegisterUser(repo)


def login_user_use_case(repo: UserRepository = Depends(get_user_repository)):
    return LoginUser(repo)


def create_category_use_case(repo: CategoryRepository = Depends(get_category_repository)):
    return CreateCategory(repo)


def list_categories_use_case(repo: CategoryRepository = Depends(get_category_repository)):
    return ListCategories(repo)


def update_category_use_case(repo: CategoryRepository = Depends(get_category_repository)):
    return UpdateCategory(repo)


def delete_category_use_case(repo: CategoryRepository = Depends(get_category_repository)):
    return DeleteCategory(repo)


def create_product_use_case(
    products: ProductRepository = Depends(get_product_repository),
    categories: CategoryRepository = Depends(get_category_repository),
):
    return CreateProduct(products, categories)


def get_product_use_case(repo: ProductRepository = Depends(get_product_repository)):
    return GetProduct(repo)


def list_products_use_case(repo: ProductRepository = Depends(get_product_repository)):
    return ListProducts(repo)


def update_product_use_case(
    products: ProductRepository = Depends(get_product_repository),
    categories: CategoryRepository = Depends(get_category_repository),
):
    return UpdateProduct(products, categories)


def update_stock_use_case(repo: ProductRepository = Depends(get_product_repository)):
    return UpdateStock(repo)


def deactivate_product_use_case(repo: ProductRepository = Depends(get_product_repository)):
    return DeactivateProduct(repo)


def add_to_cart_use_case(
    carts: CartRepository = Depends(get_cart_repository),
    products: ProductRepository = Depends(get_product_repository),
):
    return AddToCart(carts, products)


def view_cart_use_case(carts: CartRepository = Depends(get_cart_repository)):
    return ViewCart(carts)


def update_cart_item_use_case(
    carts: CartRepository = Depends(get_cart_repository),
    products: ProductRepository = Depends(get_product_repository),
):
    return UpdateCartItem(carts, products)


def remove_cart_item_use_case(carts: CartRepository = Depends(get_cart_repository)):
    return RemoveCartItem(carts)


def clear_cart_use_case(carts: CartRepository = Depends(get_cart_repository)):
    return ClearCart(carts)


def checkout_use_case(repo: OrderRepository = Depends(get_order_repository)):
    return Checkout(repo)


def get_my_order_use_case(repo: OrderRepository = Depends(get_order_repository)):
    return GetMyOrder(repo)


def list_my_orders_use_case(repo: OrderRepository = Depends(get_order_repository)):
    return ListMyOrders(repo)


def cancel_my_order_use_case(repo: OrderRepository = Depends(get_order_repository)):
    return CancelMyOrder(repo)


def admin_list_orders_use_case(repo: OrderRepository = Depends(get_order_repository)):
    return AdminListOrders(repo)


def admin_get_order_use_case(repo: OrderRepository = Depends(get_order_repository)):
    return AdminGetOrder(repo)


def update_order_status_use_case(
    orders: OrderRepository = Depends(get_order_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
):
    return UpdateOrderStatus(orders, payments)


def submit_payment_proof_use_case(
    payments: PaymentRepository = Depends(get_payment_repository),
    storage: ReceiptStorage = Depends(get_receipt_storage),
):
    return SubmitPaymentProof(payments, storage)


def get_my_payment_use_case(
    payments: PaymentRepository = Depends(get_payment_repository),
    orders: OrderRepository = Depends(get_order_repository),
):
    return GetMyPayment(payments, orders)


def admin_list_payments_use_case(repo: PaymentRepository = Depends(get_payment_repository)):
    return AdminListPayments(repo)


def admin_get_payment_use_case(repo: PaymentRepository = Depends(get_payment_repository)):
    return AdminGetPayment(repo)


def get_receipt_file_use_case(
    payments: PaymentRepository = Depends(get_payment_repository),
    storage: ReceiptStorage = Depends(get_receipt_storage),
):
    return GetReceiptFile(payments, storage)


def approve_payment_use_case(repo: PaymentRepository = Depends(get_payment_repository)):
    return ApprovePayment(repo)


def reject_payment_use_case(repo: PaymentRepository = Depends(get_payment_repository)):
    return RejectPayment(repo)


def create_coupon_use_case(repo: CouponRepository = Depends(get_coupon_repository)):
    return CreateCoupon(repo)


def list_coupons_use_case(repo: CouponRepository = Depends(get_coupon_repository)):
    return ListCoupons(repo)


def get_coupon_use_case(repo: CouponRepository = Depends(get_coupon_repository)):
    return GetCoupon(repo)


def update_coupon_use_case(repo: CouponRepository = Depends(get_coupon_repository)):
    return UpdateCoupon(repo)


def deactivate_coupon_use_case(repo: CouponRepository = Depends(get_coupon_repository)):
    return DeactivateCoupon(repo)


# ---------- Guards ----------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    repo: UserRepository = Depends(get_user_repository),
) -> User:
    # Guard 1: authentication. One message for every failure.
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise unauthorized
    user = repo.get_by_id(user_id)
    if user is None:
        raise unauthorized
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    # Guard 2: authorization. The role comes from the database, never the client.
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator permission required",
        )
    return current_user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    repo: UserRepository = Depends(get_user_repository),
) -> Optional[User]:
    # For public endpoints: a valid token is used if present, otherwise None
    if credentials is None:
        return None
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        return None
    return repo.get_by_id(user_id)