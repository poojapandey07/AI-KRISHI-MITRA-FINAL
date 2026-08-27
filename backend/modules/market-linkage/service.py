from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from config.database import db_manager
from shared.utils.security import generate_id
from .schema import (
    MarketPriceItem, BuyerOpportunityItem, BuyerConnectRequest,
    BuyerConnectResponse, MarketDashboardSummary
)

class MarketService:
    def get_market_prices(
        self,
        crop: Optional[str] = None,
        location: Optional[str] = None,
        market: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = {}
        if crop and crop.strip():
            query["crop"] = {"$regex": crop.strip(), "$options": "i"}
        if location and location.strip():
            query["$or"] = [
                {"state": {"$regex": location.strip(), "$options": "i"}},
                {"district": {"$regex": location.strip(), "$options": "i"}}
            ]
        if market and market.strip():
            query["mandi"] = {"$regex": market.strip(), "$options": "i"}

        prices = list(db_manager.market_prices.find(query))
        for p in prices:
            p["_id"] = str(p["_id"])
        return prices

    def get_buyers(
        self,
        crop: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = {}
        if crop and crop.strip():
            query["cropRequirement"] = {"$regex": crop.strip(), "$options": "i"}
        if status_filter and status_filter.strip() and status_filter.lower() != "all":
            query["status"] = {"$regex": status_filter.strip(), "$options": "i"}

        buyers = list(db_manager.buyers.find(query))
        for b in buyers:
            b["_id"] = str(b["_id"])
        return buyers

    def connect_with_buyer(
        self,
        buyer_id: str,
        farmer_id: str,
        req: BuyerConnectRequest
    ) -> BuyerConnectResponse:
        buyer = db_manager.buyers.find_one({"buyerId": buyer_id})
        if not buyer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyer listing not found.")

        farmer = db_manager.farmers.find_one({"farmerId": farmer_id})
        farmer_name = farmer.get("fullName", "Farmer") if farmer else "Farmer"
        farmer_mobile = farmer.get("mobile", "") if farmer else ""

        connection_id = generate_id("CONN", 5)

        # Store lead/connection in database
        try:
            db_manager.db.buyer_connections.insert_one({
                "connectionId": connection_id,
                "buyerId": buyer_id,
                "farmerId": farmer_id,
                "farmerName": farmer_name,
                "farmerMobile": farmer_mobile,
                "quantityOfferedQuintals": req.quantityOfferedQuintals,
                "expectedPrice": req.expectedPricePerQuintal,
                "farmerNote": req.farmerNote,
                "status": "Lead Submitted",
                "created_at": datetime.now(timezone.utc)
            })
        except Exception:
            pass

        return BuyerConnectResponse(
            connectionId=connection_id,
            buyerId=buyer_id,
            companyName=buyer["companyName"],
            status="Lead Submitted",
            message=f"Interest successfully submitted to {buyer['companyName']}. Sourcing agent will contact you on {farmer_mobile} within 24 hours."
        )

    def get_market_dashboard(self, farmer_id: Optional[str] = None) -> MarketDashboardSummary:
        # All prices
        all_prices = list(db_manager.market_prices.find())
        for p in all_prices:
            p["_id"] = str(p["_id"])

        # Gainers
        gainers = [p for p in all_prices if p.get("trend") == "up"]
        if not gainers:
            gainers = all_prices[:3]

        # Buyers
        buyers = list(db_manager.buyers.find())
        for b in buyers:
            b["_id"] = str(b["_id"])

        # Farmer specific crops
        farmer_crop_names = []
        if farmer_id:
            crops_cursor = db_manager.crops.find({"farmerId": farmer_id})
            farmer_crop_names = [c.get("cropName") for c in crops_cursor]

        farmer_prices = []
        if farmer_crop_names:
            farmer_prices = [p for p in all_prices if any(fc.lower() in p.get("crop", "").lower() for fc in farmer_crop_names)]
        if not farmer_prices:
            farmer_prices = all_prices[:4]

        return MarketDashboardSummary(
            totalMandisCovered=len(set(p.get("mandi") for p in all_prices)),
            topPriceGainers=[MarketPriceItem(**p) for p in gainers[:3]],
            activeBuyerOpportunities=[BuyerOpportunityItem(**b) for b in buyers[:4]],
            farmerCropPrices=[MarketPriceItem(**p) for p in farmer_prices]
        )

market_service = MarketService()
