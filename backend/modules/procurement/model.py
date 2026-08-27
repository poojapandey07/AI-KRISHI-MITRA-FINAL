from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

class ProcurementCentreModel:
    def __init__(self, data: Dict[str, Any]):
        self.centreId: str = data.get("centreId")
        self.name: str = data.get("name")
        self.state: str = data.get("state")
        self.district: str = data.get("district")
        self.address: str = data.get("address")
        self.availableCrops: List[str] = data.get("availableCrops", [])
        self.schedule: str = data.get("schedule")
        self.dailyCapacityQuintals: float = float(data.get("dailyCapacityQuintals", 5000))
        self.activeSlots: List[str] = data.get("activeSlots", [])
        self.contactPerson: str = data.get("contactPerson")
        self.contactPhone: str = data.get("contactPhone")
        self.status: str = data.get("status", "Operational")
        self.created_at: datetime = data.get("created_at", datetime.now(timezone.utc))

class ProcurementApplicationModel:
    def __init__(self, data: Dict[str, Any]):
        self.applicationId: str = data.get("applicationId")
        self.procurementId: str = data.get("procurementId")
        self.farmerId: str = data.get("farmerId")
        self.centreId: str = data.get("centreId")
        self.centreName: str = data.get("centreName")
        self.cropId: str = data.get("cropId")
        self.cropName: str = data.get("cropName")
        self.variety: str = data.get("variety", "")
        self.quantityQuintals: float = float(data.get("quantityQuintals", 0.0))
        self.bookingDate: str = data.get("bookingDate")
        self.timeSlot: str = data.get("timeSlot")
        self.tokenNumber: str = data.get("tokenNumber")
        self.queuePosition: int = int(data.get("queuePosition", 1))
        self.estimatedWaitMinutes: int = int(data.get("estimatedWaitMinutes", 30))
        self.status: str = data.get("status", "Application Submitted")
        self.qualityGrade: Optional[str] = data.get("qualityGrade")
        self.moisturePercent: Optional[float] = data.get("moisturePercent")
        self.ratePerQuintal: Optional[float] = data.get("ratePerQuintal")
        self.totalAmount: Optional[float] = data.get("totalAmount")
        self.created_at: datetime = data.get("created_at", datetime.now(timezone.utc))
