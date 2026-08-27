from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

class FarmerModel:
    def __init__(self, data: Dict[str, Any]):
        self.farmerId: str = data.get("farmerId")
        self.fullName: str = data.get("fullName")
        self.mobile: str = data.get("mobile")
        self.email: Optional[str] = data.get("email")
        self.hashedPassword: str = data.get("hashedPassword")
        self.state: str = data.get("state")
        self.district: str = data.get("district")
        self.village: str = data.get("village")
        self.created_at: datetime = data.get("created_at", datetime.now(timezone.utc))
        self.updated_at: datetime = data.get("updated_at", datetime.now(timezone.utc))

class LandModel:
    def __init__(self, data: Dict[str, Any]):
        self.landId: str = data.get("landId")
        self.farmerId: str = data.get("farmerId")
        self.area: float = float(data.get("area", 0.0))
        self.unit: str = data.get("unit", "Acres")
        self.soilType: str = data.get("soilType")
        self.irrigationType: str = data.get("irrigationType")
        self.location: str = data.get("location")
        self.created_at: datetime = data.get("created_at", datetime.now(timezone.utc))

class CropModel:
    def __init__(self, data: Dict[str, Any]):
        self.cropId: str = data.get("cropId")
        self.farmerId: str = data.get("farmerId")
        self.cropName: str = data.get("cropName")
        self.variety: str = data.get("variety")
        self.sowingDate: str = data.get("sowingDate")
        self.expectedHarvest: str = data.get("expectedHarvest")
        self.cultivatedArea: float = float(data.get("cultivatedArea", 0.0))
        self.areaUnit: str = data.get("areaUnit", "Acres")
        self.estimatedYieldQuintals: Optional[float] = data.get("estimatedYieldQuintals")
        self.created_at: datetime = data.get("created_at", datetime.now(timezone.utc))
