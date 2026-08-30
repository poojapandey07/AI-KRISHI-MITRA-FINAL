from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TreatmentAction(BaseModel):
    organicTreatment: List[str]
    chemicalRemedy: List[str]
    preventiveMeasures: List[str]
    urgencyText: str

class AreaCostCalculationRequest(BaseModel):
    crop: str
    disease: str
    area: float = Field(..., gt=0, description="Cultivated land area")
    unit: str = Field("Acre", description="'Acre', 'Hectare', or 'Bigha'")

class AreaCostCalculationResponse(BaseModel):
    crop: str
    disease: str
    inputArea: float
    inputUnit: str
    standardAreaAcres: float
    waterVolumeLiters: float
    managementMethod: str
    productInformation: str
    recommendedRate: float
    rateUnit: str
    requiredQuantityTotal: float
    quantityDisplay: str
    estimatedCostINR: float
    costDisplay: str
    safetyNotes: str
    source: str

class CropHealthFullResponse(BaseModel):
    analysisId: str
    crop: str = "Crop"
    health_status: str = "Diseased"
    disease_or_pest: str = "Condition"
    confidence: float = 90.0
    severity: str = "Moderate"
    risk_level: str = "Moderate"
    affected_part: str = "Leaf"
    visual_observations: List[str] = Field(default_factory=list)
    contextual_risk_analysis: str = ""
    reasoning_summary: str = ""
    farmer_friendly_explanation_en: str = ""
    farmer_friendly_explanation_hi: str = ""
    follow_up_questions: List[str] = Field(default_factory=list)
    expert_review_required: bool = False
    ai_engine: str = "Gemini 2.5 Flash"
    immediate_action: str = ""
    organic_management: Dict[str, Any] = Field(default_factory=dict)
    chemical_management: Dict[str, Any] = Field(default_factory=dict)
    prevention_steps: List[str] = Field(default_factory=list)
    monitoring_guidance: str = ""
    area_cost_estimation: Optional[AreaCostCalculationResponse] = None
    created_at: Optional[str] = None
    imageUrl: Optional[str] = None
    
    # Backward compatibility fields for previous frontend bindings
    cropDetected: Optional[str] = None
    possibleDisease: Optional[str] = None
    symptoms: Optional[List[str]] = None
    recommendedAction: Optional[TreatmentAction] = None

class DiseaseAnalysisResponse(CropHealthFullResponse):
    """Alias for backwards compatibility with existing frontend callers."""
    pass

class ExpertReviewSubmission(BaseModel):
    analysisId: str
    expertDiagnosis: str
    severity: Optional[str] = None
    expertNotes: str
    confirmAiPrediction: bool = True

class ExpertReviewItem(BaseModel):
    analysisId: str
    farmerId: Optional[str] = None
    crop: str
    aiPrediction: str
    confidence: float
    severity: str
    riskLevel: str
    expertStatus: str  # "Pending", "Verified", "Corrected"
    expertDiagnosis: Optional[str] = None
    expertNotes: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

class RegionalRiskItem(BaseModel):
    pathology: str
    reportsCount: int
    percentage: float

class RegionalRiskReportResponse(BaseModel):
    state: str
    district: str
    crop: str
    overallRiskLevel: str  # "Low", "Moderate", "High", "Critical"
    riskBadgeColor: str   # "success", "warning", "danger"
    totalReportsLast30Days: int
    weeklyTrend: str       # "Rising", "Stable", "Declining"
    topPathologies: List[RegionalRiskItem]
    earlyWarningMessage: str
    advisoryAlert: str
