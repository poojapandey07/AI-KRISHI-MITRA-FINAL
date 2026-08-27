from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class TreatmentAction(BaseModel):
    organicTreatment: List[str]
    chemicalRemedy: List[str]
    preventiveMeasures: List[str]
    urgencyText: str

class DiseaseAnalysisResponse(BaseModel):
    analysisId: str
    cropDetected: str
    possibleDisease: str
    confidence: float  # Percentage (e.g. 94.5)
    severity: str  # "Healthy", "Low", "Moderate", "High", "Critical"
    symptoms: List[str]
    recommendedAction: TreatmentAction
    created_at: Optional[str] = None
    imageUrl: Optional[str] = None
