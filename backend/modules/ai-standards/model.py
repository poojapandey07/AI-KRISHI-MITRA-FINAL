from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

class StandardsCheckRecord:
    def __init__(self, data: Dict[str, Any]):
        self.checkId: str = data.get("checkId")
        self.farmerId: Optional[str] = data.get("farmerId")
        self.crop: str = data.get("crop")
        self.variety: Optional[str] = data.get("variety")
        self.moisturePercent: float = float(data.get("moisturePercent", 0.0))
        self.foreignMatterPercent: float = float(data.get("foreignMatterPercent", 0.0))
        self.damagedGrainsPercent: float = float(data.get("damagedGrainsPercent", 0.0))
        self.assignedGrade: str = data.get("assignedGrade")
        self.isProcurementEligible: bool = bool(data.get("isProcurementEligible", True))
        self.created_at: datetime = data.get("created_at", datetime.now(timezone.utc))
