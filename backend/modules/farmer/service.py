from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from config.database import db_manager
from shared.utils.security import hash_password, verify_password, create_access_token, generate_id
from .schema import (
    FarmerRegisterRequest, FarmerLoginRequest, FarmerProfileUpdateRequest,
    AddLandRequest, AddCropRequest
)

class FarmerService:
    def register_farmer(self, req: FarmerRegisterRequest) -> Dict[str, Any]:
        # Check if mobile exists
        existing_mobile = db_manager.farmers.find_one({"mobile": req.mobile.strip()})
        if existing_mobile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A farmer account with this mobile number is already registered."
            )
        
        # Check if email exists (if provided)
        if req.email and req.email.strip():
            existing_email = db_manager.farmers.find_one({"email": req.email.strip().lower()})
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A farmer account with this email address is already registered."
                )

        farmer_id = generate_id("FMR", 6)
        now = datetime.now(timezone.utc)
        
        farmer_doc = {
            "farmerId": farmer_id,
            "fullName": req.fullName.strip(),
            "mobile": req.mobile.strip(),
            "email": req.email.strip().lower() if req.email else None,
            "hashedPassword": hash_password(req.password),
            "state": req.state.strip(),
            "district": req.district.strip(),
            "village": req.village.strip(),
            "created_at": now,
            "updated_at": now
        }
        
        db_manager.farmers.insert_one(farmer_doc)
        token = create_access_token({"sub": farmer_id, "name": req.fullName})
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "farmerId": farmer_id,
            "fullName": req.fullName,
            "mobile": req.mobile
        }

    def login_farmer(self, req: FarmerLoginRequest) -> Dict[str, Any]:
        query = req.mobileOrEmail.strip()
        farmer = db_manager.farmers.find_one({
            "$or": [
                {"mobile": query},
                {"email": query.lower()},
                {"farmerId": query}
            ]
        })
        
        if not farmer or not verify_password(req.password, farmer.get("hashedPassword", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid mobile/email or password."
            )

        token = create_access_token({"sub": farmer["farmerId"], "name": farmer["fullName"]})
        return {
            "access_token": token,
            "token_type": "bearer",
            "farmerId": farmer["farmerId"],
            "fullName": farmer["fullName"],
            "mobile": farmer["mobile"]
        }

    def get_profile(self, farmer_id: str) -> Dict[str, Any]:
        farmer = db_manager.farmers.find_one({"farmerId": farmer_id}, {"hashedPassword": 0})
        if not farmer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found.")
        
        farmer["_id"] = str(farmer["_id"])
        # Aggregate total land
        land_records = list(db_manager.land_records.find({"farmerId": farmer_id}))
        total_land = sum(l.get("area", 0) for l in land_records)
        
        # Aggregate crops count
        crops_count = db_manager.crops.count_documents({"farmerId": farmer_id})
        
        farmer["totalLandAcres"] = round(total_land, 2)
        farmer["totalCropsCount"] = crops_count
        return farmer

    def update_profile(self, farmer_id: str, req: FarmerProfileUpdateRequest) -> Dict[str, Any]:
        update_data = {k: v.strip() for k, v in req.model_dump().items() if v is not None}
        if not update_data:
            return self.get_profile(farmer_id)
            
        update_data["updated_at"] = datetime.now(timezone.utc)
        db_manager.farmers.update_one({"farmerId": farmer_id}, {"$set": update_data})
        return self.get_profile(farmer_id)

    # Land Operations
    def add_land(self, farmer_id: str, req: AddLandRequest) -> Dict[str, Any]:
        land_id = generate_id("LND", 5)
        now = datetime.now(timezone.utc)
        doc = {
            "landId": land_id,
            "farmerId": farmer_id,
            "area": float(req.area),
            "unit": req.unit,
            "soilType": req.soilType,
            "irrigationType": req.irrigationType,
            "location": req.location,
            "created_at": now
        }
        db_manager.land_records.insert_one(doc)
        doc["_id"] = str(doc["_id"])
        doc["created_at"] = doc["created_at"].isoformat()
        return doc

    def get_farmer_land(self, farmer_id: str) -> List[Dict[str, Any]]:
        records = list(db_manager.land_records.find({"farmerId": farmer_id}))
        for r in records:
            r["_id"] = str(r["_id"])
            if isinstance(r.get("created_at"), datetime):
                r["created_at"] = r["created_at"].isoformat()
        return records

    # Crop Operations
    def add_crop(self, farmer_id: str, req: AddCropRequest) -> Dict[str, Any]:
        crop_id = generate_id("CRP", 5)
        now = datetime.now(timezone.utc)
        doc = {
            "cropId": crop_id,
            "farmerId": farmer_id,
            "cropName": req.cropName,
            "variety": req.variety,
            "sowingDate": req.sowingDate,
            "expectedHarvest": req.expectedHarvest,
            "cultivatedArea": float(req.cultivatedArea),
            "areaUnit": req.areaUnit,
            "estimatedYieldQuintals": req.estimatedYieldQuintals,
            "created_at": now
        }
        db_manager.crops.insert_one(doc)
        doc["_id"] = str(doc["_id"])
        doc["created_at"] = doc["created_at"].isoformat()
        return doc

    def get_farmer_crops(self, farmer_id: str) -> List[Dict[str, Any]]:
        crops = list(db_manager.crops.find({"farmerId": farmer_id}))
        for c in crops:
            c["_id"] = str(c["_id"])
            if isinstance(c.get("created_at"), datetime):
                c["created_at"] = c["created_at"].isoformat()
        return crops

farmer_service = FarmerService()
