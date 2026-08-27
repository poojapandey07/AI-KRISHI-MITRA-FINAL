from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

class MarketPriceModel:
    def __init__(self, data: Dict[str, Any]):
        self.crop: str = data.get("crop")
        self.variety: str = data.get("variety", "")
        self.mandi: str = data.get("mandi")
        self.district: str = data.get("district")
        self.state: str = data.get("state")
        self.modalPrice: float = float(data.get("modalPrice", 0.0))
        self.minPrice: float = float(data.get("minPrice", 0.0))
        self.maxPrice: float = float(data.get("maxPrice", 0.0))
        self.unit: str = data.get("unit", "₹ / Quintal")
        self.msp: Optional[float] = data.get("msp")
        self.trend: str = data.get("trend", "flat")
        self.change: str = data.get("change", "₹0")
        self.arrivalVolumeQuintals: Optional[float] = data.get("arrivalVolumeQuintals")
        self.lastUpdated: str = data.get("lastUpdated")

class BuyerOpportunityModel:
    def __init__(self, data: Dict[str, Any]):
        self.buyerId: str = data.get("buyerId")
        self.companyName: str = data.get("companyName")
        self.category: str = data.get("category")
        self.cropRequirement: str = data.get("cropRequirement")
        self.preferredVariety: str = data.get("preferredVariety")
        self.requiredQuantity: str = data.get("requiredQuantity")
        self.indicativePrice: float = float(data.get("indicativePrice", 0.0))
        self.unit: str = data.get("unit", "₹ / Quintal")
        self.location: str = data.get("location")
        self.qualitySpecifications: str = data.get("qualitySpecifications")
        self.paymentTerms: str = data.get("paymentTerms")
        self.status: str = data.get("status", "Open")
        self.contactEmail: str = data.get("contactEmail")
        self.contactPhone: str = data.get("contactPhone")
        self.created_at: datetime = data.get("created_at", datetime.now(timezone.utc))
