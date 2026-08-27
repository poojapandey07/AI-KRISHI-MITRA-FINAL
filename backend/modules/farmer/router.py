from fastapi import APIRouter, Depends, status
from typing import List, Dict, Any
from middleware.auth import get_current_farmer
from shared.schemas.common import ApiResponse
from .schema import (
    FarmerRegisterRequest, FarmerLoginRequest, TokenResponse,
    FarmerProfileResponse, FarmerProfileUpdateRequest,
    AddLandRequest, LandResponse, AddCropRequest, CropResponse
)
from .service import farmer_service

auth_router = APIRouter()
farmer_router = APIRouter()

# ----------------- Auth Endpoints ----------------- #

@auth_router.post("/register", response_model=ApiResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
def register(req: FarmerRegisterRequest):
    result = farmer_service.register_farmer(req)
    return ApiResponse(
        success=True,
        message="Farmer registered successfully. Welcome to AI Krishi Mitra!",
        data=TokenResponse(**result)
    )

@auth_router.post("/login", response_model=ApiResponse[TokenResponse])
def login(req: FarmerLoginRequest):
    result = farmer_service.login_farmer(req)
    return ApiResponse(
        success=True,
        message="Login successful.",
        data=TokenResponse(**result)
    )

@auth_router.get("/me", response_model=ApiResponse[FarmerProfileResponse])
def get_current_user_profile(farmer: dict = Depends(get_current_farmer)):
    profile = farmer_service.get_profile(farmer["farmerId"])
    return ApiResponse(
        success=True,
        message="Profile retrieved successfully.",
        data=FarmerProfileResponse(**profile)
    )

# ----------------- Farmer Profile & Farm Endpoints ----------------- #

@farmer_router.get("/profile", response_model=ApiResponse[FarmerProfileResponse])
def get_profile(farmer: dict = Depends(get_current_farmer)):
    profile = farmer_service.get_profile(farmer["farmerId"])
    return ApiResponse(
        success=True,
        message="Farmer profile loaded.",
        data=FarmerProfileResponse(**profile)
    )

@farmer_router.put("/profile", response_model=ApiResponse[FarmerProfileResponse])
def update_profile(req: FarmerProfileUpdateRequest, farmer: dict = Depends(get_current_farmer)):
    profile = farmer_service.update_profile(farmer["farmerId"], req)
    return ApiResponse(
        success=True,
        message="Farmer profile updated successfully.",
        data=FarmerProfileResponse(**profile)
    )

@farmer_router.get("/land", response_model=ApiResponse[List[LandResponse]])
def list_land(farmer: dict = Depends(get_current_farmer)):
    records = farmer_service.get_farmer_land(farmer["farmerId"])
    return ApiResponse(
        success=True,
        message="Land records retrieved.",
        data=[LandResponse(**r) for r in records]
    )

@farmer_router.post("/land", response_model=ApiResponse[LandResponse], status_code=status.HTTP_201_CREATED)
def add_land(req: AddLandRequest, farmer: dict = Depends(get_current_farmer)):
    doc = farmer_service.add_land(farmer["farmerId"], req)
    return ApiResponse(
        success=True,
        message="Land record added successfully.",
        data=LandResponse(**doc)
    )

@farmer_router.get("/crops", response_model=ApiResponse[List[CropResponse]])
def list_crops(farmer: dict = Depends(get_current_farmer)):
    crops = farmer_service.get_farmer_crops(farmer["farmerId"])
    return ApiResponse(
        success=True,
        message="Crops retrieved.",
        data=[CropResponse(**c) for c in crops]
    )

@farmer_router.post("/crops", response_model=ApiResponse[CropResponse], status_code=status.HTTP_201_CREATED)
def add_crop(req: AddCropRequest, farmer: dict = Depends(get_current_farmer)):
    doc = farmer_service.add_crop(farmer["farmerId"], req)
    return ApiResponse(
        success=True,
        message="Crop registered successfully.",
        data=CropResponse(**doc)
    )
