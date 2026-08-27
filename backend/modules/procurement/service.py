import random
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from config.database import db_manager
from shared.utils.security import generate_id
from .schema import BookSlotRequest, UpdateProcurementStatusRequest

# Default MSP / Mandi rates per quintal for fallback rate calculation
DEFAULT_CROP_RATES = {
    "Wheat": 2425.0,
    "Paddy": 2203.0,
    "Paddy (Basmati)": 3850.0,
    "Mustard": 5650.0,
    "Cotton": 7200.0,
    "Soyabean": 4650.0,
    "Chana (Chickpea)": 5800.0,
    "Maize": 2150.0,
    "Tomato": 1800.0,
    "Onion": 2350.0
}

VALID_STATUSES = [
    "Application Submitted",
    "Slot Confirmed",
    "Produce Received",
    "Quality Checked",
    "Procurement Accepted",
    "Payment Initiated"
]

class ProcurementService:
    def list_centres(self, crop: Optional[str] = None, state: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {"status": "Operational"}
        if crop and crop.strip():
            query["availableCrops"] = {"$regex": crop.strip(), "$options": "i"}
        if state and state.strip():
            query["state"] = {"$regex": state.strip(), "$options": "i"}
            
        centres = list(db_manager.procurement_centres.find(query))
        for c in centres:
            c["_id"] = str(c["_id"])
        return centres

    def book_slot(self, farmer_id: str, req: BookSlotRequest) -> Dict[str, Any]:
        # 1. Verify centre
        centre = db_manager.procurement_centres.find_one({"centreId": req.centreId})
        if not centre:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Procurement centre not found.")

        # 2. Verify crop
        crop = db_manager.crops.find_one({"cropId": req.cropId, "farmerId": farmer_id})
        crop_name = crop.get("cropName", "Unknown Crop") if crop else "General Produce"
        variety = crop.get("variety", "") if crop else ""

        # 3. Generate identifiers
        app_id = generate_id("APP", 5)
        prc_id = generate_id("PRC", 5)
        token_num = f"TKN-{random.randint(10, 99)}"
        
        # Calculate queue position based on existing bookings on that date/slot
        existing_count = db_manager.procurement_applications.count_documents({
            "centreId": req.centreId,
            "bookingDate": req.bookingDate,
            "timeSlot": req.timeSlot
        })
        queue_pos = existing_count + 1
        est_wait = queue_pos * 15  # approx 15 mins per farmer

        now = datetime.now(timezone.utc)
        rate = DEFAULT_CROP_RATES.get(crop_name, 2200.0)
        total_amount = round(req.quantityQuintals * rate, 2)

        application_doc = {
            "applicationId": app_id,
            "procurementId": prc_id,
            "farmerId": farmer_id,
            "centreId": req.centreId,
            "centreName": centre.get("name"),
            "cropId": req.cropId,
            "cropName": crop_name,
            "variety": variety,
            "quantityQuintals": float(req.quantityQuintals),
            "bookingDate": req.bookingDate,
            "timeSlot": req.timeSlot,
            "tokenNumber": token_num,
            "queuePosition": queue_pos,
            "estimatedWaitMinutes": est_wait,
            "status": "Application Submitted",
            "qualityGrade": None,
            "moisturePercent": None,
            "ratePerQuintal": rate,
            "totalAmount": total_amount,
            "created_at": now
        }

        db_manager.procurement_applications.insert_one(application_doc)
        application_doc["_id"] = str(application_doc["_id"])
        application_doc["created_at"] = application_doc["created_at"].isoformat()
        return application_doc

    def get_farmer_applications(self, farmer_id: str) -> List[Dict[str, Any]]:
        apps = list(db_manager.procurement_applications.find({"farmerId": farmer_id}).sort("created_at", -1))
        for a in apps:
            a["_id"] = str(a["_id"])
            if isinstance(a.get("created_at"), datetime):
                a["created_at"] = a["created_at"].isoformat()
        return apps

    def get_queue_status(self, application_id: str) -> Dict[str, Any]:
        app = db_manager.procurement_applications.find_one({"applicationId": application_id})
        if not app:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Procurement application not found.")
        
        return {
            "applicationId": app["applicationId"],
            "procurementId": app["procurementId"],
            "tokenNumber": app["tokenNumber"],
            "queuePosition": app.get("queuePosition", 1),
            "estimatedWaitMinutes": app.get("estimatedWaitMinutes", 15),
            "status": app["status"],
            "centreName": app["centreName"],
            "timeSlot": app["timeSlot"]
        }

    def update_application_status(self, application_id: str, req: UpdateProcurementStatusRequest) -> Dict[str, Any]:
        app = db_manager.procurement_applications.find_one({"applicationId": application_id})
        if not app:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Procurement application not found.")

        if req.status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status '{req.status}'. Must be one of: {', '.join(VALID_STATUSES)}"
            )

        update_fields: Dict[str, Any] = {"status": req.status}
        if req.qualityGrade:
            update_fields["qualityGrade"] = req.qualityGrade
        if req.moisturePercent is not None:
            update_fields["moisturePercent"] = req.moisturePercent
        if req.ratePerQuintal is not None:
            update_fields["ratePerQuintal"] = req.ratePerQuintal
            update_fields["totalAmount"] = round(app.get("quantityQuintals", 0.0) * req.ratePerQuintal, 2)

        # Update queue position if progressing past token phase
        if req.status in ["Produce Received", "Quality Checked", "Procurement Accepted", "Payment Initiated"]:
            update_fields["queuePosition"] = 0
            update_fields["estimatedWaitMinutes"] = 0

        db_manager.procurement_applications.update_one(
            {"applicationId": application_id},
            {"$set": update_fields}
        )

        updated_app = db_manager.procurement_applications.find_one({"applicationId": application_id})

        # CRITICAL INTEGRATION:
        # When procurement reaches Payment Initiated, connect it to the Finance module.
        if req.status == "Payment Initiated":
            self._trigger_finance_payment(updated_app)

        updated_app["_id"] = str(updated_app["_id"])
        if isinstance(updated_app.get("created_at"), datetime):
            updated_app["created_at"] = updated_app["created_at"].isoformat()
        return updated_app

    def _trigger_finance_payment(self, app_doc: dict):
        """Cross-module trigger to initiate Finance payment tracking."""
        procurement_id = app_doc["procurementId"]
        existing_payment = db_manager.payments.find_one({"procurementId": procurement_id})
        if existing_payment:
            return  # Already linked

        farmer_id = app_doc["farmerId"]
        # Find farmer's bank account
        bank_acc = db_manager.bank_accounts.find_one({"farmerId": farmer_id})
        
        bank_id = bank_acc.get("bankAccountId") if bank_acc else None
        bank_name = bank_acc.get("bankName") if bank_acc else "Pending Bank Link"
        masked_acc = bank_acc.get("maskedAccountNumber") if bank_acc else "Not Linked"

        payment_id = generate_id("PAY", 5)
        now = datetime.now(timezone.utc)
        amount = app_doc.get("totalAmount") or (app_doc.get("quantityQuintals", 0.0) * app_doc.get("ratePerQuintal", 2200.0))

        payment_doc = {
            "paymentId": payment_id,
            "procurementId": procurement_id,
            "applicationId": app_doc["applicationId"],
            "farmerId": farmer_id,
            "crop": app_doc.get("cropName", "Produce"),
            "quantityQuintals": app_doc.get("quantityQuintals", 0.0),
            "ratePerQuintal": app_doc.get("ratePerQuintal", 2200.0),
            "amount": round(amount, 2),
            "bankAccountId": bank_id,
            "bankName": bank_name,
            "maskedAccountNumber": masked_acc,
            "status": "Payment Initiated",
            "initiatedAt": now.isoformat(),
            "creditedAt": None,
            "remarks": f"Direct procurement payout for {app_doc.get('quantityQuintals')} Quintals {app_doc.get('cropName')} at {app_doc.get('centreName')}",
            "created_at": now
        }
        db_manager.payments.insert_one(payment_doc)

procurement_service = ProcurementService()
