from typing import Optional
from pydantic import BaseModel, Field

class LinkBankAccountRequest(BaseModel):
    bankName: str = Field(..., min_length=2)
    accountHolder: str = Field(..., min_length=2)
    accountNumber: str = Field(..., min_length=9, max_length=18)
    ifscCode: str = Field(..., min_length=11, max_length=11)

class BankAccountResponse(BaseModel):
    bankAccountId: str
    farmerId: str
    bankName: str
    accountHolder: str
    maskedAccountNumber: str
    ifscCode: str
    branchName: Optional[str] = None
    verificationStatus: str  # "Not Verified", "Verification Pending", "Verified", "Verification Failed"
    verifiedAt: Optional[str] = None
    created_at: Optional[str] = None

class VerifyBankRequest(BaseModel):
    bankAccountId: str
    action: str = Field(default="verify")  # "verify" or "fail" for sandbox testing

class PaymentResponse(BaseModel):
    paymentId: str
    procurementId: str
    applicationId: Optional[str] = None
    farmerId: str
    crop: str
    quantityQuintals: float
    ratePerQuintal: float
    amount: float
    bankAccountId: Optional[str] = None
    bankName: Optional[str] = None
    maskedAccountNumber: Optional[str] = None
    status: str  # "Payment Initiated", "Payment Processing", "Payment Credited", "Payment Failed"
    initiatedAt: Optional[str] = None
    creditedAt: Optional[str] = None
    remarks: Optional[str] = None
    date: Optional[str] = None

class SimulatePaymentStatusRequest(BaseModel):
    status: str  # "Payment Processing", "Payment Credited", "Payment Failed"
