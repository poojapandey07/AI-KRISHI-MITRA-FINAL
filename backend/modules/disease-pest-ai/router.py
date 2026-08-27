from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import List, Optional
from middleware.auth import get_optional_farmer, get_current_farmer
from shared.schemas.common import ApiResponse
from .schema import DiseaseAnalysisResponse
from .service import disease_ai_service

router = APIRouter()

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/jpg"]

@router.post("", response_model=ApiResponse[DiseaseAnalysisResponse])
@router.post("/", response_model=ApiResponse[DiseaseAnalysisResponse])
async def analyze_crop_disease(
    file: UploadFile = File(...),
    farmer: Optional[dict] = Depends(get_optional_farmer)
):
    if file.content_type and file.content_type.lower() not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{file.content_type}'. Please upload a JPEG, PNG, or WEBP image."
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded image file is empty."
        )

    farmer_id = farmer.get("farmerId") if farmer else None
    result = disease_ai_service.analyze_crop_image(content, file.filename or "crop_sample.jpg", farmer_id)

    return ApiResponse(
        success=True,
        message=f"Diagnosis completed: Detected {result.cropDetected} - {result.possibleDisease} ({result.confidence}% confidence).",
        data=result
    )

@router.get("/history", response_model=ApiResponse[List[DiseaseAnalysisResponse]])
def get_history(farmer: dict = Depends(get_current_farmer)):
    history = disease_ai_service.get_analysis_history(farmer["farmerId"])
    return ApiResponse(
        success=True,
        message=f"Retrieved {len(history)} previous disease diagnosis scans.",
        data=history
    )
