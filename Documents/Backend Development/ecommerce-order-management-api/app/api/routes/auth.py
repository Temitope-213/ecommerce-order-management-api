from fastapi import APIRouter, Depends, status

from app.api.dependencies import login_user_use_case, register_user_use_case
from app.application.use_cases.login_user import LoginUser
from app.application.use_cases.register_user import RegisterUser
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(
    data: UserCreate,
    use_case: RegisterUser = Depends(register_user_use_case),
):
    return use_case.execute(data.username, data.email, data.password)


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    use_case: LoginUser = Depends(login_user_use_case),
):
    token = use_case.execute(data.email, data.password)
    return {"access_token": token, "token_type": "bearer"}