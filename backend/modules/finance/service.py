import re
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from config.database import db_manager
from shared.utils.security import generate_id, mask_account_number
from .schema import LinkBankAccountRequest, VerifyBankRequest

VALID_PAYMENT_STATUSES = [
    "Payment Initiated",
    "Payment Processing",
    "Payment Credited",
    "Payment Failed"
]

class FinanceService:
    def get_farmer_bank(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        acc = db_manager.bank_accounts.find_one({"farmerId": farmer_id})
        if not acc:
            return None
        return self._format_bank_account(acc)

    def link_bank_account(self, farmer_id: str, req: LinkBankAccountRequest) -> Dict[str, Any]:
        # Validate IFSC format (4 letters, 0, 6 alphanumeric)
        clean_ifsc = req.ifscCode.strip().upper()
        if not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", clean_ifsc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid IFSC format. Example: SBIN0001234, HDFC0000123"
            )

        clean_acc = req.accountNumber.strip()
        if not clean_acc.isdigit() or len(clean_acc) < 9 or len(clean_acc) > 18:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account number must contain 9 to 18 digits."
            )

        # Check if already exists for this farmer
        existing = db_manager.bank_accounts.find_one({"farmerId": farmer_id})
        bank_id = existing["bankAccountId"] if existing else generate_id("BNK", 5)
        now = datetime.now(timezone.utc)

        doc = {
            "bankAccountId": bank_id,
            "farmerId": farmer_id,
            "bankName": req.bankName.strip(),
            "accountHolder": req.accountHolder.strip(),
            "accountNumber": clean_acc,  # Securely stored
            "maskedAccountNumber": mask_account_number(clean_acc),
            "ifscCode": clean_ifsc,
            "branchName": f"{clean_ifsc[:4]} Agricultural Branch",
            "verificationStatus": "Verification Pending",
            "verifiedAt": None,
            "updated_at": now
        }

        if existing:
            db_manager.bank_accounts.update_one({"farmerId": farmer_id}, {"$set": doc})
        else:
            doc["created_at"] = now
            db_manager.bank_accounts.insert_one(doc)

        saved = db_manager.bank_accounts.find_one({"farmerId": farmer_id})
        return self._format_bank_account(saved)

    def verify_bank_account(self, farmer_id: str, req: VerifyBankRequest) -> Dict[str, Any]:
        """
        Mock / Sandbox verification service layer.
        Simulates NPCI / Penny-drop micro-deposit bank account verification.
        """
        acc = db_manager.bank_accounts.find_one({
            "farmerId": farmer_id,
            "bankAccountId": req.bankAccountId
        })
        if not acc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank account record not found."
            )

        now = datetime.now(timezone.utc)
        if req.action == "fail":
            new_status = "Verification Failed"
            verified_at = None
        else:
            new_status = "Verified"
            verified_at = now.isoformat()

        db_manager.bank_accounts.update_one(
            {"bankAccountId": req.bankAccountId},
            {"$set": {
                "verificationStatus": new_status,
                "verifiedAt": verified_at,
                "updated_at": now
            }}
        )

        updated = db_manager.bank_accounts.find_one({"bankAccountId": req.bankAccountId})
        return self._format_bank_account(updated)

    def list_farmer_payments(self, farmer_id: str, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {"farmerId": farmer_id}
        if status_filter and status_filter.lower() != "all":
            filter_val = status_filter.strip().lower()
            if filter_val == "processing":
                query["status"] = "Payment Processing"
            elif filter_val == "credited":
                query["status"] = "Payment Credited"
            elif filter_val == "failed":
                query["status"] = "Payment Failed"
            elif filter_val == "initiated":
                query["status"] = "Payment Initiated"

        payments = list(db_manager.payments.find(query).sort("created_at", -1))
        formatted = []
        for p in payments:
            p["_id"] = str(p["_id"])
            p["date"] = p.get("initiatedAt") or (p.get("created_at").strftime("%Y-%m-%d") if isinstance(p.get("created_at"), datetime) else "")
            formatted.append(p)
        return formatted

    def simulate_payment_status(self, payment_id: str, new_status: str) -> Dict[str, Any]:
        if new_status not in VALID_PAYMENT_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment status. Must be one of: {', '.join(VALID_PAYMENT_STATUSES)}"
            )

        payment = db_manager.payments.find_one({"paymentId": payment_id})
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found.")

        update_fields: Dict[str, Any] = {"status": new_status}
        if new_status == "Payment Credited":
            update_fields["creditedAt"] = datetime.now(timezone.utc).isoformat()
            update_fields["remarks"] = "Direct DBT settlement credited successfully to farmer bank account."

        db_manager.payments.update_one({"paymentId": payment_id}, {"$set": update_fields})
        updated = db_manager.payments.find_one({"paymentId": payment_id})
        updated["_id"] = str(updated["_id"])
        updated["date"] = updated.get("initiatedAt")
        return updated

    def _format_bank_account(self, acc: dict) -> dict:
        result = dict(acc)
        result["_id"] = str(result["_id"])
        # Ensure raw account number is NEVER exposed in the API response
        result.pop("accountNumber", None)
        if isinstance(result.get("created_at"), datetime):
            result["created_at"] = result["created_at"].isoformat()
        return result

finance_service = FinanceService()
