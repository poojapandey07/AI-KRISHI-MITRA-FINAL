from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

class DiseaseAnalysisRecord:
    def __init__(self, data: Dict[str, Any]):
        self.analysisId: str = data.get("analysisId")
        self.farmerId: Optional[str] = data.get("farmerId")
        self.filename: str = data.get("filename")
        self.cropDetected: str = data.get("cropDetected")
        self.possibleDisease: str = data.get("possibleDisease")
        self.confidence: float = float(data.get("confidence", 0.0))
        self.severity: str = data.get("severity")  # "Low", "Moderate", "High", "Critical", "Healthy"
        self.recommendedAction: Dict[str, Any] = data.get("recommendedAction", {})
        self.created_at: datetime = data.get("created_at", datetime.now(timezone.utc))
