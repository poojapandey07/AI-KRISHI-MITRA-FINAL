from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from middleware.auth import get_optional_farmer, get_current_farmer
from shared.schemas.common import ApiResponse
from .schema import (
    MarketPriceItem, BuyerOpportunityItem, BuyerConnectRequest,
    BuyerConnectResponse, MarketDashboardSummary
)
from .service import market_service

router = APIRouter()

@router.get("/prices", response_model=ApiResponse[List[MarketPriceItem]])
def get_prices(
    crop: Optional[str] = Query(None, description="Search by crop name"),
    location: Optional[str] = Query(None, description="Search by state or district"),
    market: Optional[str] = Query(None, description="Search by mandi name")
):
    prices = market_service.get_market_prices(crop=crop, location=location, market=market)
    return ApiResponse(
        success=True,
        message=f"Found {len(prices)} mandi price listings.",
        data=[MarketPriceItem(**p) for p in prices]
    )

@router.get("/buyers", response_model=ApiResponse[List[BuyerOpportunityItem]])
def get_buyers(
    crop: Optional[str] = Query(None, description="Filter buyers by crop"),
    status: Optional[str] = Query(None, description="Filter by status (Open, Urgent, Accepting Bids)")
):
    buyers = market_service.get_buyers(crop=crop, status_filter=status)
    return ApiResponse(
        success=True,
        message=f"Found {len(buyers)} corporate/institutional buyer opportunities.",
        data=[BuyerOpportunityItem(**b) for b in buyers]
    )

@router.post("/buyers/{buyerId}/connect", response_model=ApiResponse[BuyerConnectResponse], status_code=status.HTTP_201_CREATED)
def connect_with_buyer(
    buyerId: str,
    req: BuyerConnectRequest,
    farmer: dict = Depends(get_current_farmer)
):
    resp = market_service.connect_with_buyer(buyerId, farmer["farmerId"], req)
    return ApiResponse(
        success=True,
        message="Buyer connection request placed successfully.",
        data=resp
    )

@router.get("/dashboard", response_model=ApiResponse[MarketDashboardSummary])
def get_market_dashboard(farmer: dict = Depends(get_optional_farmer)):
    farmer_id = farmer.get("farmerId") if farmer else None
    summary = market_service.get_market_dashboard(farmer_id)
    return ApiResponse(
        success=True,
        message="Market overview summary loaded.",
        data=summary
    )
