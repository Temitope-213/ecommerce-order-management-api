from fastapi import APIRouter, Depends, Path, Response, status

from app.api.dependencies import (
    add_to_cart_use_case,
    clear_cart_use_case,
    get_current_user,
    remove_cart_item_use_case,
    update_cart_item_use_case,
    view_cart_use_case,
)
from app.application.use_cases.manage_cart import (
    AddToCart,
    ClearCart,
    RemoveCartItem,
    UpdateCartItem,
    ViewCart,
)
from app.domain.entities.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse

router = APIRouter(prefix="/cart", tags=["Shopping Cart"])


# The cart owner always comes from the token (current_user), never from the URL
# or request body, so a customer can never reach another customer's cart.


@router.get("", response_model=CartResponse)
def view_cart(
    use_case: ViewCart = Depends(view_cart_use_case),
    current_user: User = Depends(get_current_user),
):
    return use_case.execute(current_user.id)


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    data: CartItemCreate,
    use_case: AddToCart = Depends(add_to_cart_use_case),
    current_user: User = Depends(get_current_user),
):
    return use_case.execute(current_user.id, data.product_id, data.quantity)


@router.put("/items/{product_id}", response_model=CartResponse)
def update_cart_item(
    data: CartItemUpdate,
    product_id: int = Path(..., gt=0),
    use_case: UpdateCartItem = Depends(update_cart_item_use_case),
    current_user: User = Depends(get_current_user),
):
    return use_case.execute(current_user.id, product_id, data.quantity)


@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    product_id: int = Path(..., gt=0),
    use_case: RemoveCartItem = Depends(remove_cart_item_use_case),
    current_user: User = Depends(get_current_user),
):
    use_case.execute(current_user.id, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    use_case: ClearCart = Depends(clear_cart_use_case),
    current_user: User = Depends(get_current_user),
):
    use_case.execute(current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)