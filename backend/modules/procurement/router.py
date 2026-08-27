from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from middleware.auth import get_current_farmer, get_optional_farmer
from shared.schemas.common import ApiResponse
from .schema import (
    ProcurementCentreResponse, BookSlotRequest, QueueStatusResponse,
    ProcurementApplicationResponse, UpdateProcurementStatusRequest
)
from .service import procurement_service

router = APIRouter()

@router.get("/centres", response_model=ApiResponse[List[ProcurementCentreResponse]])
def get_centres(
    crop: Optional[str] = Query(None, description="Filter by crop name"),
    state: Optional[str] = Query(None, description="Filter by state")
):
    centres = procurement_service.list_centres(crop=crop, state=state)
    return ApiResponse(
        success=True,
        message=f"Found {len(centres)} procurement centres.",
        data=[ProcurementCentreResponse(**c) for c in centres]
    )

@router.post("/applications", response_model=ApiResponse[ProcurementApplicationResponse], status_code=status.HTTP_201_CREATED)
def book_procurement_slot(req: BookSlotRequest, farmer: dict = Depends(get_current_farmer)):
    doc = procurement_service.book_slot(farmer["farmerId"], req)
    return ApiResponse(
        success=True,
        message="Procurement slot booked successfully! Token and queue assigned.",
        data=ProcurementApplicationResponse(**doc)
    )

@router.get("/applications", response_model=ApiResponse[List[ProcurementApplicationResponse]])
def get_farmer_applications(farmer: dict = Depends(get_current_farmer)):
    apps = procurement_service.get_farmer_applications(farmer["farmerId"])
    return ApiResponse(
        success=True,
        message="Procurement applications retrieved.",
        data=[ProcurementApplicationResponse(**a) for a in apps]
    )

@router.get("/queue/{applicationId}", response_model=ApiResponse[QueueStatusResponse])
def get_queue_status(applicationId: str, farmer: dict = Depends(get_current_farmer)):
    status_info = procurement_service.get_queue_status(applicationId)
    return ApiResponse(
        success=True,
        message="Live queue status retrieved.",
        data=QueueStatusResponse(**status_info)
    )

@router.patch("/applications/{applicationId}/status", response_model=ApiResponse[ProcurementApplicationResponse])
def update_status(
    applicationId: str,
    req: UpdateProcurementStatusRequest,
    farmer: dict = Depends(get_current_farmer)
):
    updated = procurement_service.update_application_status(applicationId, req)
    return ApiResponse(
        success=True,
        message=f"Procurement application status updated to '{req.status}'.",
        data=ProcurementApplicationResponse(**updated)
    )
