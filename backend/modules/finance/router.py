from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from middleware.auth import get_current_farmer
from shared.schemas.common import ApiResponse
from .schema import (
    LinkBankAccountRequest, BankAccountResponse, VerifyBankRequest,
    PaymentResponse, SimulatePaymentStatusRequest
)
from .service import finance_service

router = APIRouter()

@router.get("/bank", response_model=ApiResponse[Optional[BankAccountResponse]])
def get_bank_details(farmer: dict = Depends(get_current_farmer)):
    bank = finance_service.get_farmer_bank(farmer["farmerId"])
    if not bank:
        return ApiResponse(
            success=True,
            message="No linked bank account found.",
            data=None
        )
    return ApiResponse(
        success=True,
        message="Linked bank account details retrieved.",
        data=BankAccountResponse(**bank)
    )

@router.post("/bank", response_model=ApiResponse[BankAccountResponse], status_code=status.HTTP_201_CREATED)
def link_bank(req: LinkBankAccountRequest, farmer: dict = Depends(get_current_farmer)):
    bank = finance_service.link_bank_account(farmer["farmerId"], req)
    return ApiResponse(
        success=True,
        message="Bank account linked successfully! Verification pending.",
        data=BankAccountResponse(**bank)
    )

@router.post("/verification", response_model=ApiResponse[BankAccountResponse])
@router.post("/bank/verify", response_model=ApiResponse[BankAccountResponse])
def verify_bank(req: VerifyBankRequest, farmer: dict = Depends(get_current_farmer)):
    bank = finance_service.verify_bank_account(farmer["farmerId"], req)
    return ApiResponse(
        success=True,
        message=f"Bank verification completed. Status: {bank['verificationStatus']}",
        data=BankAccountResponse(**bank)
    )

@router.get("/payments", response_model=ApiResponse[List[PaymentResponse]])
def list_payments(
    status: Optional[str] = Query(None, description="Filter: all, processing, credited, failed, initiated"),
    farmer: dict = Depends(get_current_farmer)
):
    payments = finance_service.list_farmer_payments(farmer["farmerId"], status_filter=status)
    return ApiResponse(
        success=True,
        message=f"Retrieved {len(payments)} payment records.",
        data=[PaymentResponse(**p) for p in payments]
    )

@router.patch("/payments/{paymentId}/simulate-status", response_model=ApiResponse[PaymentResponse])
def simulate_payment(
    paymentId: str,
    req: SimulatePaymentStatusRequest,
    farmer: dict = Depends(get_current_farmer)
):
    updated = finance_service.simulate_payment_status(paymentId, req.status)
    return ApiResponse(
        success=True,
        message=f"Payment status updated to {req.status}",
        data=PaymentResponse(**updated)
    )
