from typing import Optional, List
from pydantic import BaseModel, Field

class ProcurementCentreResponse(BaseModel):
    centreId: str
    name: str
    state: str
    district: str
    address: str
    availableCrops: List[str]
    schedule: str
    dailyCapacityQuintals: float
    activeSlots: List[str]
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    status: str

class BookSlotRequest(BaseModel):
    centreId: str
    cropId: str
    quantityQuintals: float = Field(..., gt=0)
    bookingDate: str
    timeSlot: str

class QueueStatusResponse(BaseModel):
    applicationId: str
    procurementId: str
    tokenNumber: str
    queuePosition: int
    estimatedWaitMinutes: int
    status: str
    centreName: str
    timeSlot: str

class ProcurementApplicationResponse(BaseModel):
    applicationId: str
    procurementId: str
    farmerId: str
    centreId: str
    centreName: str
    cropId: str
    cropName: str
    variety: Optional[str] = None
    quantityQuintals: float
    bookingDate: str
    timeSlot: str
    tokenNumber: str
    queuePosition: int
    estimatedWaitMinutes: int
    status: str
    qualityGrade: Optional[str] = None
    moisturePercent: Optional[float] = None
    ratePerQuintal: Optional[float] = None
    totalAmount: Optional[float] = None
    created_at: Optional[str] = None

class UpdateProcurementStatusRequest(BaseModel):
    status: str  # e.g. "Slot Confirmed", "Produce Received", "Quality Checked", "Procurement Accepted", "Payment Initiated"
    qualityGrade: Optional[str] = None
    moisturePercent: Optional[float] = None
    ratePerQuintal: Optional[float] = None
