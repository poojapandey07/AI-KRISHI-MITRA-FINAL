from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class QualityCheckRequest(BaseModel):
    crop: str = Field(..., min_length=2)
    variety: Optional[str] = None
    moisturePercent: float = Field(..., ge=0, le=100, description="Moisture percentage")
    foreignMatterPercent: float = Field(default=0.5, ge=0, le=50, description="Foreign matter %")
    damagedGrainsPercent: float = Field(default=1.0, ge=0, le=50, description="Damaged/discolored %")
    brokenGrainsPercent: Optional[float] = Field(default=2.0, ge=0, le=50)

class StandardParameterComparison(BaseModel):
    parameter: str
    farmerValue: float
    maxAllowedFCI: float
    unit: str
    status: str  # "Pass", "Warning", "Fail"
    recommendation: str

class StandardsResultResponse(BaseModel):
    crop: str
    variety: Optional[str] = None
    assignedGrade: str  # e.g. "Grade A (Premium)", "FAQ (Fair Average Quality)", "Below Standard"
    isProcurementEligible: bool
    qualityScore: int  # 0 to 100
    mspPriceExpected: float
    priceImpactText: str
    comparisons: List[StandardParameterComparison]
    handlingAdvice: List[str]
    storageAdvice: List[str]
    dryingTechnique: str

class CropRecommendationItem(BaseModel):
    category: str  # "Quality", "Handling", "Storage", "Procurement", "Market"
    crop: str
    title: str
    summary: str
    actionSteps: List[str]
    priority: str  # "High", "Medium", "Seasonal"
