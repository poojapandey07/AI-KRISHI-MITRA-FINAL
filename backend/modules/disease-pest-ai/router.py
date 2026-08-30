from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any

from middleware.auth import get_optional_farmer, get_current_farmer
from shared.schemas.common import ApiResponse
from .schema import (
    CropHealthFullResponse,
    DiseaseAnalysisResponse,
    AreaCostCalculationRequest,
    AreaCostCalculationResponse,
    ExpertReviewSubmission,
    ExpertReviewItem,
    RegionalRiskReportResponse
)
from .service import crop_health_service
from .recommendations_data import find_recommendation

router = APIRouter()

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/jpg"]

# ----------------- 1. Main Multimodal Crop Analysis ----------------- #

@router.post("/analyze", response_model=ApiResponse[CropHealthFullResponse], tags=["5. Disease & Pest AI"])
@router.post("", response_model=ApiResponse[CropHealthFullResponse], tags=["5. Disease & Pest AI"])
@router.post("/", response_model=ApiResponse[CropHealthFullResponse], tags=["5. Disease & Pest AI"])
async def analyze_crop(
    file: UploadFile = File(...),
    crop: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),
    farmArea: Optional[float] = Form(None),
    areaUnit: Optional[str] = Form("Acre"),
    state: Optional[str] = Form(None),
    district: Optional[str] = Form(None),
    growthStage: Optional[str] = Form(None),
    language: Optional[str] = Form("en"),
    farmer: Optional[dict] = Depends(get_optional_farmer)
):
    """
    Main Multimodal Crop Health Analysis endpoint.
    Sends image + context to Gemini API (or calibrated fallback engine).
    Validates output, looks up ICAR/CIBRC treatments, calculates deterministic area/cost,
    and returns rich vernacular diagnosis report.
    """
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

    # If farmer is logged in and state/district wasn't provided in form, use profile location
    farmer_id = farmer.get("farmerId") if farmer else None
    farmer_state = state or (farmer.get("state") if farmer else None)
    farmer_district = district or (farmer.get("district") if farmer else None)

    result = crop_health_service.analyze_crop_image(
        image_bytes=content,
        filename=file.filename or "crop_sample.jpg",
        farmer_id=farmer_id,
        crop_hint=crop,
        symptoms=symptoms,
        farm_area=farmArea,
        area_unit=areaUnit,
        state=farmer_state,
        district=farmer_district,
        growth_stage=growthStage,
        language=language or "en"
    )

    msg = f"Diagnosis complete: Detected {result.crop} - {result.disease_or_pest} ({result.confidence}% confidence)."
    if result.expert_review_required:
        msg += " AI confidence is low; diagnosis has been flagged for agricultural specialist verification."

    return ApiResponse(
        success=True,
        message=msg,
        data=result
    )

# ----------------- 2. Re-Analyze with Contextual Feedback ----------------- #

@router.post("/reanalyze", response_model=ApiResponse[CropHealthFullResponse], tags=["5. Disease & Pest AI"])
async def reanalyze_crop(
    file: UploadFile = File(...),
    crop: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),
    farmArea: Optional[float] = Form(None),
    areaUnit: Optional[str] = Form("Acre"),
    state: Optional[str] = Form(None),
    district: Optional[str] = Form(None),
    growthStage: Optional[str] = Form(None),
    clarifyingAnswers: Optional[str] = Form(None),
    farmer: Optional[dict] = Depends(get_optional_farmer)
):
    """Re-runs diagnosis incorporating the farmer's clarifying answers for medium confidence cases."""
    combined_symptoms = f"{symptoms or ''} [Follow-up context: {clarifyingAnswers or ''}]".strip()
    return await analyze_crop(
        file=file,
        crop=crop,
        symptoms=combined_symptoms,
        farmArea=farmArea,
        areaUnit=areaUnit,
        state=state,
        district=district,
        growthStage=growthStage,
        farmer=farmer
    )

# ----------------- 3. Farmer History Timeline ----------------- #

@router.get("/history", response_model=ApiResponse[List[CropHealthFullResponse]], tags=["5. Disease & Pest AI"])
def get_crop_history(farmer: dict = Depends(get_current_farmer)):
    """Fetch chronological diagnosis history for the authenticated farmer."""
    history = crop_health_service.get_analysis_history(farmer["farmerId"])
    return ApiResponse(
        success=True,
        message=f"Retrieved {len(history)} previous diagnosis scans.",
        data=history
    )

# ----------------- 4. Single Analysis Lookup ----------------- #

@router.get("/analysis/{analysis_id}", response_model=ApiResponse[CropHealthFullResponse], tags=["5. Disease & Pest AI"])
def get_analysis_by_id(analysis_id: str):
    """Retrieve full details of a specific crop health diagnostic report."""
    analysis = crop_health_service.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return ApiResponse(
        success=True,
        message="Analysis report retrieved successfully.",
        data=analysis
    )

# ----------------- 5. Deterministic Area & Cost Calculator ----------------- #

@router.post("/calculate-cost", response_model=ApiResponse[AreaCostCalculationResponse], tags=["5. Disease & Pest AI"])
def calculate_cost(req: AreaCostCalculationRequest):
    """
    Deterministic backend calculation for required spray volume, chemical quantity,
    and estimated cost in INR based on validated ICAR guidelines.
    """
    calc = crop_health_service.calculate_area_and_cost(
        crop=req.crop,
        disease=req.disease,
        area=req.area,
        unit=req.unit
    )
    return ApiResponse(
        success=True,
        message=f"Treatment estimation calculated for {req.area} {req.unit}.",
        data=calc
    )

# ----------------- 6. Validated Agricultural Recommendation ----------------- #

@router.get("/recommendation/{disease}", response_model=ApiResponse[Dict[str, Any]], tags=["5. Disease & Pest AI"])
def get_recommendation(disease: str, crop: Optional[str] = None):
    """Retrieve authoritative ICAR/CIBRC validated agricultural protocol for a disease."""
    rec = find_recommendation(crop, disease)
    return ApiResponse(
        success=True,
        message=f"Retrieved validated agricultural recommendation for '{disease}'.",
        data=rec
    )

# ----------------- 7. Regional Disease Risk & Early Warning ----------------- #

@router.get("/risk", response_model=ApiResponse[RegionalRiskReportResponse], tags=["5. Disease & Pest AI"])
def get_regional_risk(
    state: Optional[str] = Query(None, description="State (e.g. Haryana, Punjab, Maharashtra)"),
    district: Optional[str] = Query(None, description="District (e.g. Karnal, Ludhiana, Nashik)"),
    crop: Optional[str] = Query(None, description="Crop filter")
):
    """
    Regional Disease Risk Engine:
    Returns aggregated anonymized disease reports, trend analysis, and early warning risk level.
    """
    risk_report = crop_health_service.get_regional_risk_report(
        state=state,
        district=district,
        crop=crop
    )
    return ApiResponse(
        success=True,
        message="Regional disease risk analysis loaded.",
        data=risk_report
    )

# ----------------- 8. Expert Review System ----------------- #

@router.post("/expert-review", response_model=ApiResponse[Dict[str, Any]], tags=["5. Disease & Pest AI"])
def submit_expert_review(submission: ExpertReviewSubmission):
    """Specialist submits diagnosis confirmation or correction."""
    res = crop_health_service.submit_expert_review(submission)
    return ApiResponse(
        success=True,
        message=res["message"],
        data=res
    )

@router.get("/expert-review/queue", response_model=ApiResponse[List[ExpertReviewItem]], tags=["5. Disease & Pest AI"])
def get_expert_queue(limit: int = Query(20, ge=1, le=100)):
    """Retrieve pending analyses requiring expert verification."""
    queue = crop_health_service.get_expert_queue(limit=limit)
    return ApiResponse(
        success=True,
        message=f"Retrieved {len(queue)} analyses pending specialist review.",
        data=queue
    )
