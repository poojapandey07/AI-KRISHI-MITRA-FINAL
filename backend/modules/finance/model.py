from datetime import datetime, timezone
from typing import Optional, Dict, Any

class BankAccountModel:
    def __init__(self, data: Dict[str, Any]):
        self.bankAccountId: str = data.get("bankAccountId")
        self.farmerId: str = data.get("farmerId")
        self.bankName: str = data.get("bankName")
        self.accountHolder: str = data.get("accountHolder")
        self.accountNumber: str = data.get("accountNumber")  # Stored internally, never exposed in full via APIs
        self.maskedAccountNumber: str = data.get("maskedAccountNumber")
        self.ifscCode: str = data.get("ifscCode")
        self.branchName: Optional[str] = data.get("branchName", "Main Branch")
        self.verificationStatus: str = data.get("verificationStatus", "Verification Pending")
        self.verifiedAt: Optional[str] = data.get("verifiedAt")
        self.created_at: datetime = data.get("created_at", datetime.now(timezone.utc))

class PaymentModel:
    def __init__(self, data: Dict[str, Any]):
        self.paymentId: str = data.get("paymentId")
        self.procurementId: str = data.get("procurementId")
        self.applicationId: Optional[str] = data.get("applicationId")
        self.farmerId: str = data.get("farmerId")
        self.crop: str = data.get("crop")
        self.quantityQuintals: float = float(data.get("quantityQuintals", 0.0))
        self.ratePerQuintal: float = float(data.get("ratePerQuintal", 0.0))
        self.amount: float = float(data.get("amount", 0.0))
        self.bankAccountId: Optional[str] = data.get("bankAccountId")
        self.bankName: Optional[str] = data.get("bankName")
        self.maskedAccountNumber: Optional[str] = data.get("maskedAccountNumber")
        self.status: str = data.get("status", "Payment Initiated")
        self.initiatedAt: str = data.get("initiatedAt")
        self.creditedAt: Optional[str] = data.get("creditedAt")
        self.remarks: Optional[str] = data.get("remarks")
        self.created_at: datetime = data.get("created_at", datetime.now(timezone.utc))
