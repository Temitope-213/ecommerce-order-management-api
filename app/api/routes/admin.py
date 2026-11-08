from fastapi import APIRouter, Depends

from app.api.dependencies import require_admin
from app.domain.entities.user import User

router = APIRouter(prefix="/admin", tags=["Admin Operations"])


@router.get("/check")
def admin_check(admin: User = Depends(require_admin)):
    return {"message": "Welcome, administrator", "email": admin.email}