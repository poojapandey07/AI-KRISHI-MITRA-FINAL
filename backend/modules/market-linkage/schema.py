from typing import Optional, List
from pydantic import BaseModel, Field

class MarketPriceItem(BaseModel):
    crop: str
    variety: Optional[str] = None
    mandi: str
    district: str
    state: str
    modalPrice: float
    minPrice: float
    maxPrice: float
    unit: str = "₹ / Quintal"
    msp: Optional[float] = None
    trend: str = "flat"  # "up", "down", "flat"
    change: str = "₹0"
    arrivalVolumeQuintals: Optional[float] = None
    lastUpdated: Optional[str] = None

class BuyerOpportunityItem(BaseModel):
    buyerId: str
    companyName: str
    category: str
    cropRequirement: str
    preferredVariety: Optional[str] = None
    requiredQuantity: str
    indicativePrice: float
    unit: str = "₹ / Quintal"
    location: str
    qualitySpecifications: Optional[str] = None
    paymentTerms: Optional[str] = None
    status: str  # "Open", "Accepting Bids", "Urgent"
    contactEmail: Optional[str] = None
    contactPhone: Optional[str] = None

class BuyerConnectRequest(BaseModel):
    quantityOfferedQuintals: float = Field(..., gt=0)
    expectedPricePerQuintal: Optional[float] = None
    farmerNote: Optional[str] = None

class BuyerConnectResponse(BaseModel):
    connectionId: str
    buyerId: str
    companyName: str
    status: str
    message: str

class MarketDashboardSummary(BaseModel):
    totalMandisCovered: int
    topPriceGainers: List[MarketPriceItem]
    activeBuyerOpportunities: List[BuyerOpportunityItem]
    farmerCropPrices: List[MarketPriceItem]
