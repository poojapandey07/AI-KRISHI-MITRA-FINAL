from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class FarmerRegisterRequest(BaseModel):
    fullName: str = Field(..., min_length=2, max_length=100)
    mobile: str = Field(..., min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)
    state: str = Field(..., min_length=2)
    district: str = Field(..., min_length=2)
    village: str = Field(..., min_length=2)

class FarmerLoginRequest(BaseModel):
    mobileOrEmail: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    farmerId: str
    fullName: str
    mobile: str

class FarmerProfileResponse(BaseModel):
    farmerId: str
    fullName: str
    mobile: str
    email: Optional[str] = None
    state: str
    district: str
    village: str
    totalLandAcres: float = 0.0
    totalCropsCount: int = 0

class FarmerProfileUpdateRequest(BaseModel):
    fullName: Optional[str] = None
    email: Optional[EmailStr] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None

class AddLandRequest(BaseModel):
    area: float = Field(..., gt=0)
    unit: str = Field(default="Acres")
    soilType: str
    irrigationType: str
    location: str

class LandResponse(BaseModel):
    landId: str
    farmerId: str
    area: float
    unit: str
    soilType: str
    irrigationType: str
    location: str
    created_at: Optional[str] = None

class AddCropRequest(BaseModel):
    cropName: str
    variety: str
    sowingDate: str
    expectedHarvest: str
    cultivatedArea: float = Field(..., gt=0)
    areaUnit: str = Field(default="Acres")
    estimatedYieldQuintals: Optional[float] = None

class CropResponse(BaseModel):
    cropId: str
    farmerId: str
    cropName: str
    variety: str
    sowingDate: str
    expectedHarvest: str
    cultivatedArea: float
    areaUnit: str
    estimatedYieldQuintals: Optional[float] = None
    created_at: Optional[str] = None
