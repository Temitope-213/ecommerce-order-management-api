from typing import Optional

from fastapi import APIRouter, Depends, File, Path, Query, UploadFile, status
from fastapi.responses import FileResponse

from app.api.dependencies import (
    admin_get_payment_use_case,
    admin_list_payments_use_case,
    approve_payment_use_case,
    get_current_user,
    get_my_payment_use_case,
    get_receipt_file_use_case,
    reject_payment_use_case,
    require_admin,
    submit_payment_proof_use_case,
)
from app.application.use_cases.manage_payments import (
    MAX_RECEIPT_BYTES,
    AdminGetPayment,
    AdminListPayments,
    ApprovePayment,
    GetMyPayment,
    GetReceiptFile,
    RejectPayment,
    SubmitPaymentProof,
)
from app.domain.entities.payment import PaymentStatus
from app.domain.entities.user import User
from app.schemas.payment import (
    AdminPaymentListResponse,
    AdminPaymentResponse,
    PaymentResponse,
    RejectPaymentRequest,
)

# ---------- Customer ----------
router = APIRouter(prefix="/orders", tags=["Payments"])


@router.post(
    "/{order_id}/payment",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_payment_proof(
    order_id: int = Path(..., gt=0),
    file: UploadFile = File(...),
    use_case: SubmitPaymentProof = Depends(submit_payment_proof_use_case),
    current_user: User = Depends(get_current_user),
):
    # Read at most 1 byte over the limit, so a huge file is never fully loaded
    content = file.file.read(MAX_RECEIPT_BYTES + 1)
    return use_case.execute(current_user.id, order_id, content)


@router.get("/{order_id}/payment", response_model=PaymentResponse)
def get_my_payment(
    order_id: int = Path(..., gt=0),
    use_case: GetMyPayment = Depends(get_my_payment_use_case),
    current_user: User = Depends(get_current_user),
):
    return use_case.execute(current_user.id, order_id)


# ---------- Admin ----------
admin_router = APIRouter(prefix="/admin/payments", tags=["Admin Operations"])


@admin_router.get("", response_model=AdminPaymentListResponse)
def list_payments(
    payment_status: Optional[PaymentStatus] = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    use_case: AdminListPayments = Depends(admin_list_payments_use_case),
    admin: User = Depends(require_admin),
):
    items, total = use_case.execute(payment_status, page, page_size)
    return AdminPaymentListResponse(
        items=items, total=total, page=page, page_size=page_size
    )


@admin_router.get("/{payment_id}", response_model=AdminPaymentResponse)
def get_payment(
    payment_id: int = Path(..., gt=0),
    use_case: AdminGetPayment = Depends(admin_get_payment_use_case),
    admin: User = Depends(require_admin),
):
    return use_case.execute(payment_id)


@admin_router.get("/{payment_id}/receipt")
def download_receipt(
    payment_id: int = Path(..., gt=0),
    use_case: GetReceiptFile = Depends(get_receipt_file_use_case),
    admin: User = Depends(require_admin),
):
    path, media_type = use_case.execute(payment_id)
    return FileResponse(path, media_type=media_type)


@admin_router.post("/{payment_id}/approve", response_model=AdminPaymentResponse)
def approve_payment(
    payment_id: int = Path(..., gt=0),
    use_case: ApprovePayment = Depends(approve_payment_use_case),
    admin: User = Depends(require_admin),
):
    return use_case.execute(admin.id, payment_id)


@admin_router.post("/{payment_id}/reject", response_model=AdminPaymentResponse)
def reject_payment(
    data: RejectPaymentRequest,
    payment_id: int = Path(..., gt=0),
    use_case: RejectPayment = Depends(reject_payment_use_case),
    admin: User = Depends(require_admin),
):
    return use_case.execute(admin.id, payment_id, data.reason)