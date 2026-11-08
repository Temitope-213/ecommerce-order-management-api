from fastapi import APIRouter, Depends

from app.api.dependencies import get_system_info_use_case, require_admin
from app.application.use_cases.get_system_info import GetSystemInfo
from app.domain.entities.user import User
from app.schemas.system_info import SystemInfoResponse

router = APIRouter(prefix="/admin", tags=["Admin Operations"])


@router.get("/check")
def admin_check(admin: User = Depends(require_admin)):
    return {"message": "Welcome, administrator", "email": admin.email}


@router.get("/system-info", response_model=SystemInfoResponse)
def system_info(
    use_case: GetSystemInfo = Depends(get_system_info_use_case),
    admin: User = Depends(require_admin),
):
    return use_case.execute()