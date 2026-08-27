from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from middleware.auth import get_optional_farmer
from shared.schemas.common import ApiResponse
from .schema import QualityCheckRequest, StandardsResultResponse, CropRecommendationItem
from .service import ai_standards_service, CROP_STANDARD_THRESHOLDS

router = APIRouter()

@router.post("/standards", response_model=ApiResponse[StandardsResultResponse])
def check_crop_standards(req: QualityCheckRequest, farmer: dict = Depends(get_optional_farmer)):
    farmer_id = farmer.get("farmerId") if farmer else None
    result = ai_standards_service.analyze_quality_and_standards(req, farmer_id)
    return ApiResponse(
        success=True,
        message=f"Quality standards assessment completed: Assigned Grade {result.assignedGrade}.",
        data=result
    )

@router.get("/recommendations", response_model=ApiResponse[List[CropRecommendationItem]])
def get_recommendations(farmer: dict = Depends(get_optional_farmer)):
    farmer_id = farmer.get("farmerId") if farmer else None
    recs = ai_standards_service.get_farmer_recommendations(farmer_id)
    return ApiResponse(
        success=True,
        message=f"Generated {len(recs)} tailored AI agricultural recommendations.",
        data=recs
    )

@router.get("/standards/catalog", response_model=ApiResponse[Dict[str, Any]])
def get_standards_catalog():
    return ApiResponse(
        success=True,
        message="Official FCI and Agmark standards catalog retrieved.",
        data=CROP_STANDARD_THRESHOLDS
    )
