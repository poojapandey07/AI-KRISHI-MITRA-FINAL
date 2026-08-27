from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from config.database import db_manager
from shared.utils.security import generate_id
from .schema import QualityCheckRequest, StandardsResultResponse, StandardParameterComparison, CropRecommendationItem

# Official FCI / Agmark procurement threshold specifications
CROP_STANDARD_THRESHOLDS = {
    "Wheat": {
        "maxMoisture": 12.0,
        "maxForeignMatter": 0.75,
        "maxDamaged": 2.0,
        "maxBroken": 4.0,
        "msp": 2275.0,
        "marketAvg": 2450.0
    },
    "Paddy": {
        "maxMoisture": 17.0,
        "maxForeignMatter": 1.0,
        "maxDamaged": 3.0,
        "maxBroken": 5.0,
        "msp": 2203.0,
        "marketAvg": 2350.0
    },
    "Paddy (Basmati)": {
        "maxMoisture": 14.0,
        "maxForeignMatter": 0.5,
        "maxDamaged": 1.5,
        "maxBroken": 2.0,
        "msp": 2203.0,
        "marketAvg": 3850.0
    },
    "Mustard": {
        "maxMoisture": 8.0,
        "maxForeignMatter": 2.0,
        "maxDamaged": 2.0,
        "maxBroken": 2.0,
        "msp": 5650.0,
        "marketAvg": 5650.0
    },
    "Maize": {
        "maxMoisture": 14.0,
        "maxForeignMatter": 1.5,
        "maxDamaged": 3.0,
        "maxBroken": 4.0,
        "msp": 2090.0,
        "marketAvg": 2150.0
    },
    "Soyabean": {
        "maxMoisture": 10.0,
        "maxForeignMatter": 2.0,
        "maxDamaged": 3.0,
        "maxBroken": 4.0,
        "msp": 4600.0,
        "marketAvg": 4650.0
    },
    "Chana (Chickpea)": {
        "maxMoisture": 10.0,
        "maxForeignMatter": 1.0,
        "maxDamaged": 3.0,
        "maxBroken": 3.0,
        "msp": 5440.0,
        "marketAvg": 5800.0
    },
    "Cotton": {
        "maxMoisture": 8.5,
        "maxForeignMatter": 1.5,
        "maxDamaged": 2.0,
        "maxBroken": 1.0,
        "msp": 7020.0,
        "marketAvg": 7200.0
    }
}

class AIStandardsService:
    def analyze_quality_and_standards(self, req: QualityCheckRequest, farmer_id: Optional[str] = None) -> StandardsResultResponse:
        crop_key = None
        for key in CROP_STANDARD_THRESHOLDS:
            if key.lower() in req.crop.lower() or req.crop.lower() in key.lower():
                crop_key = key
                break
        if not crop_key:
            crop_key = "Wheat"  # Default reference standard

        specs = CROP_STANDARD_THRESHOLDS[crop_key]
        comparisons: List[StandardParameterComparison] = []
        score = 100
        eligible = True

        # 1. Moisture Analysis
        m_diff = req.moisturePercent - specs["maxMoisture"]
        if m_diff <= 0:
            m_status = "Pass"
            m_rec = f"Optimal moisture ({req.moisturePercent}% <= {specs['maxMoisture']}%). Grain is safe from fungal rot."
        elif m_diff <= 1.5:
            m_status = "Warning"
            score -= 15
            m_rec = f"Slightly elevated (+{m_diff:.1f}%). Sun dry on clean tarpaulin for 4-6 daylight hours before dispatch."
        else:
            m_status = "Fail"
            score -= 35
            eligible = False
            m_rec = f"Excess moisture (+{m_diff:.1f}%). High risk of mandi rejection or heavy value deductions. Immediate aeration required."

        comparisons.append(StandardParameterComparison(
            parameter="Moisture Content",
            farmerValue=req.moisturePercent,
            maxAllowedFCI=specs["maxMoisture"],
            unit="%",
            status=m_status,
            recommendation=m_rec
        ))

        # 2. Foreign Matter Analysis
        fm_diff = req.foreignMatterPercent - specs["maxForeignMatter"]
        if fm_diff <= 0:
            fm_status = "Pass"
            fm_rec = "Excellent cleanliness, within Agmark Grade 1 specifications."
        elif fm_diff <= 1.0:
            fm_status = "Warning"
            score -= 10
            fm_rec = "Light dust/chaff present. Pass through mechanical seed cleaner or wire winnowing screen."
        else:
            fm_status = "Fail"
            score -= 25
            eligible = False
            fm_rec = f"Elevated foreign matter ({req.foreignMatterPercent}% vs max {specs['maxForeignMatter']}%). Requires secondary sieving."

        comparisons.append(StandardParameterComparison(
            parameter="Foreign Matter (Dust & Chaff)",
            farmerValue=req.foreignMatterPercent,
            maxAllowedFCI=specs["maxForeignMatter"],
            unit="%",
            status=fm_status,
            recommendation=fm_rec
        ))

        # 3. Damaged / Discolored Grains
        dmg_diff = req.damagedGrainsPercent - specs["maxDamaged"]
        if dmg_diff <= 0:
            dmg_status = "Pass"
            dmg_rec = "Grain luster and kernel integrity meet FCI Fair Average Quality benchmarks."
        elif dmg_diff <= 1.5:
            dmg_status = "Warning"
            score -= 10
            dmg_rec = "Mild discoloration detected. Separate weeviled kernels using gravity separator."
        else:
            dmg_status = "Fail"
            score -= 25
            eligible = False
            dmg_rec = f"Damaged kernels exceed limit ({req.damagedGrainsPercent}% vs max {specs['maxDamaged']}%)."

        comparisons.append(StandardParameterComparison(
            parameter="Damaged & Discolored Kernels",
            farmerValue=req.damagedGrainsPercent,
            maxAllowedFCI=specs["maxDamaged"],
            unit="%",
            status=dmg_status,
            recommendation=dmg_rec
        ))

        score = max(score, 10)

        # Grade Assignment
        if eligible and score >= 85:
            grade = "Grade A (FAQ Passed)"
            price_impact = f"Eligible for 100% full MSP (₹{specs['msp']}/Q) or premium private buyer rate (₹{specs['marketAvg']}/Q)."
        elif eligible and score >= 65:
            grade = "FAQ (Fair Average Quality)"
            price_impact = f"Approved for Government Procurement at baseline MSP (₹{specs['msp']}/Q) without deductions."
        else:
            grade = "Below Standard (Needs Pre-Conditioning)"
            eligible = False
            price_impact = f"Subject to ₹70 - ₹120/Quintal price discount at Mandi unless dried and cleaned first."

        # Handling & Storage Advice
        handling_advice = [
            f"Thresh {crop_key} during dry midday hours to avoid collecting dew moisture.",
            "Use clean, food-grade HDPE tarpaulins during sun drying; never place grain directly on raw mud soil.",
            "Ensure harvesting combine blades are calibrated to avoid cracking wheat/paddy grains."
        ]

        storage_advice = [
            "Store in clean, sanitized multi-layer hermetic bags (PICS bags) to prevent moisture re-absorption and weevil attack.",
            "Stack bags at least 15 cm above the floor on wooden pallets with 50 cm clearance from walls for airflow.",
            "Inspect grain temperature and smell weekly; if moisture rises above threshold, aerate immediately."
        ]

        drying_tech = (
            f"Thin-layer open air solar drying on canvas: Spread to 4-5 cm depth, stir every 45 minutes for 4 hours. "
            f"Expected moisture reduction: ~1.2% per 3 sunshine hours."
        )

        # Save check record if farmer is authenticated
        if farmer_id:
            try:
                db_manager.ai_recommendations.insert_one({
                    "checkId": generate_id("CHK", 5),
                    "farmerId": farmer_id,
                    "crop": req.crop,
                    "variety": req.variety,
                    "grade": grade,
                    "score": score,
                    "eligible": eligible,
                    "created_at": datetime.now(timezone.utc)
                })
            except Exception:
                pass

        return StandardsResultResponse(
            crop=req.crop,
            variety=req.variety,
            assignedGrade=grade,
            isProcurementEligible=eligible,
            qualityScore=score,
            mspPriceExpected=specs["msp"],
            priceImpactText=price_impact,
            comparisons=comparisons,
            handlingAdvice=handling_advice,
            storageAdvice=storage_advice,
            dryingTechnique=drying_tech
        )

    def get_farmer_recommendations(self, farmer_id: Optional[str] = None) -> List[CropRecommendationItem]:
        # Collect farmer's active crops
        farmer_crops = []
        if farmer_id:
            crops_cursor = db_manager.crops.find({"farmerId": farmer_id})
            farmer_crops = [c.get("cropName") for c in crops_cursor]

        if not farmer_crops:
            farmer_crops = ["Wheat", "Mustard"]

        recommendations: List[CropRecommendationItem] = []

        for crop in farmer_crops:
            if "wheat" in crop.lower():
                recommendations.extend([
                    CropRecommendationItem(
                        category="Procurement",
                        crop="Wheat",
                        title="Optimal Harvest & Mandi Window Approaching",
                        summary="Government APMC centres opening early procurement windows with zero queue booking.",
                        actionSteps=[
                            "Harvest when moisture reads between 11.5% and 12.0%.",
                            "Book an online procurement slot at Karnal APMC Hub 3 days in advance.",
                            "Keep bank account verified to enable direct T+2 DBT payment."
                        ],
                        priority="High"
                    ),
                    CropRecommendationItem(
                        category="Quality",
                        crop="Wheat",
                        title="Prevent Post-Harvest Black Tip Discoloration",
                        summary="Sudden late humidity or damp storage can lead to fungal black tip degrading grade to FAQ-Below.",
                        actionSteps=[
                            "Avoid bagging grains harvested after sudden morning rain until 4 hours of sun drying.",
                            "Do not mix old stock with fresh 2025 harvest."
                        ],
                        priority="Medium"
                    ),
                    CropRecommendationItem(
                        category="Market",
                        crop="Wheat",
                        title="ITC & Private Millers Offering ₹150/Q Above MSP",
                        summary="Private corporate buyers are actively looking for HD-2967 & Sharbati quality lots with protein > 12%.",
                        actionSteps=[
                            "Check Buyer Linkage tab for direct factory pickup offers.",
                            "Request free moisture testing at procurement gate before final sale."
                        ],
                        priority="High"
                    )
                ])
            elif "mustard" in crop.lower():
                recommendations.extend([
                    CropRecommendationItem(
                        category="Storage",
                        crop="Mustard",
                        title="Maintain Moisture Under 8% for High Oil Value",
                        summary="Mustard oil extractors deduct price sharply if seed moisture exceeds 8.0%.",
                        actionSteps=[
                            "Sun dry seeds thoroughly on clean tarpaulin.",
                            "Store in gunny bags lined with polythene in dry, shaded godown."
                        ],
                        priority="High"
                    ),
                    CropRecommendationItem(
                        category="Market",
                        crop="Mustard",
                        title="Patanjali Agro Active Sourcing in Haryana & Rajasthan",
                        summary="High demand for Bold Variety mustard offering direct payment settlement within 24h.",
                        actionSteps=[
                            "Inspect listing in Market Linkage module.",
                            "Submit contact request directly through the portal."
                        ],
                        priority="Seasonal"
                    )
                ])
            else:
                recommendations.append(
                    CropRecommendationItem(
                        category="Quality",
                        crop=crop,
                        title=f"Standard Handling Guidelines for {crop}",
                        summary=f"Follow regulated Agmark post-harvest handling to maximize procurement grade for {crop}.",
                        actionSteps=[
                            "Store in clean, pest-free bags on wooden elevation pallets.",
                            "Check live Mandi rates on the Market tab before scheduling harvest dispatch."
                        ],
                        priority="Medium"
                    )
                )

        return recommendations

ai_standards_service = AIStandardsService()
