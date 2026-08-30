import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from config.database import db_manager
from shared.utils.security import generate_id
from services.ai.gemini_service import gemini_crop_service
from .recommendations_data import find_recommendation, VALIDATED_RECOMMENDATIONS
from .schema import (
    CropHealthFullResponse,
    AreaCostCalculationRequest,
    AreaCostCalculationResponse,
    TreatmentAction,
    ExpertReviewSubmission,
    ExpertReviewItem,
    RegionalRiskReportResponse,
    RegionalRiskItem
)

logger = logging.getLogger("ai_krishi_mitra.crop_service")

class CropHealthService:
    def __init__(self):
        self.gemini_service = gemini_crop_service

    def analyze_crop_image(
        self,
        image_bytes: bytes,
        filename: str,
        farmer_id: Optional[str] = None,
        crop_hint: Optional[str] = None,
        symptoms: Optional[str] = None,
        farm_area: Optional[float] = None,
        area_unit: Optional[str] = "Acre",
        state: Optional[str] = None,
        district: Optional[str] = None,
        growth_stage: Optional[str] = None,
        language: str = "en"
    ) -> CropHealthFullResponse:
        """
        Orchestrates full Crop Health Intelligence flow:
        1. Gemini Multimodal Analysis (or Calibrated Heuristic Engine fallback)
        2. Strict Confidence-Aware Logic (<0.60 auto-flags expert review)
        3. Authoritative Validated Agricultural Recommendations
        4. Deterministic Area & Cost Calculator
        5. Vernacular Translation formatting
        6. MongoDB Persistence
        """
        now = datetime.now(timezone.utc)
        analysis_id = generate_id("DIS", 5)

        # 1. Perform Gemini Multimodal Analysis
        ai_res = self.gemini_service.analyze_crop_image(
            image_bytes=image_bytes,
            filename=filename,
            crop_hint=crop_hint,
            symptoms=symptoms,
            farm_area=farm_area,
            area_unit=area_unit,
            state=state,
            district=district,
            growth_stage=growth_stage
        )

        detected_crop = ai_res.get("crop") or crop_hint or "Tomato"
        detected_disease = ai_res.get("disease_or_pest") or "Early Blight"
        raw_confidence = float(ai_res.get("confidence", 0.88))
        # Ensure confidence is between 0 and 100 for display, normalized float for checks
        norm_conf = raw_confidence if raw_confidence <= 1.0 else (raw_confidence / 100.0)
        display_confidence = round(norm_conf * 100.0, 1)

        severity = ai_res.get("severity", "Moderate")
        health_status = ai_res.get("health_status", "Diseased")
        risk_level = ai_res.get("risk_level", "Moderate")
        affected_part = ai_res.get("affected_part", "Leaf")
        visual_obs = ai_res.get("visual_observations", ["Foliar lesion observed"])
        context_risk = ai_res.get("contextual_risk_analysis", f"Environmental risk monitored in {district or 'field'}.")
        reasoning = ai_res.get("reasoning_summary", "Foliar pathology diagnosed from image.")
        exp_en = ai_res.get("farmer_friendly_explanation_en", "Crop symptoms detected. Follow management protocol.")
        exp_hi = ai_res.get("farmer_friendly_explanation_hi", "फसल में बीमारी के लक्षण दिखे हैं। नीचे दिए गए प्रबंधन उपाय देखें।")
        follow_ups = ai_res.get("follow_up_questions", [])

        # 2. Confidence-Aware Rule Enforcement
        # IF confidence < 0.60: Low confidence -> Auto-queue for Expert Review
        expert_review_required = norm_conf < 0.60 or ai_res.get("expert_review_required", False)

        # 3. Retrieve Validated Agricultural Recommendation (ICAR / CIBRC standards)
        validated_rec = find_recommendation(detected_crop, detected_disease)

        # 4. Deterministic Area & Cost Calculation
        calc_area = farm_area if (farm_area and farm_area > 0) else 1.0
        calc_unit = area_unit or "Acre"
        cost_estimation = self.calculate_area_and_cost(
            crop=detected_crop,
            disease=detected_disease,
            area=calc_area,
            unit=calc_unit
        )

        # 5. Build TreatmentAction for backwards compatibility
        org_mgmt = validated_rec.get("organic_management", {})
        chem_mgmt = validated_rec.get("chemical_management", {})
        prev_steps = validated_rec.get("prevention_steps", [])

        organic_list = [
            f"{org_mgmt.get('product_information', 'Neem formulation')} @ {org_mgmt.get('recommended_rate', '')} {org_mgmt.get('unit', '')}",
            f"Safety note: {org_mgmt.get('safety_notes', 'Safe bio-input.')}"
        ]
        chem_list = [
            f"{chem_mgmt.get('product_information', 'Standard protectant')} @ {chem_mgmt.get('recommended_rate', '')} {chem_mgmt.get('unit', '')}",
            f"Water ref: {chem_mgmt.get('water_reference_per_acre', 180)} L/Acre. {chem_mgmt.get('safety_notes', '')}"
        ]

        treatment_action = TreatmentAction(
            organicTreatment=organic_list,
            chemicalRemedy=chem_list,
            preventiveMeasures=prev_steps,
            urgencyText=validated_rec.get("immediate_action", "Inspect foliage closely.")
        )

        # 6. Assemble Full Response Model
        response_data = CropHealthFullResponse(
            analysisId=analysis_id,
            crop=detected_crop,
            health_status=health_status,
            disease_or_pest=detected_disease,
            confidence=display_confidence,
            severity=severity,
            risk_level=risk_level,
            affected_part=affected_part,
            visual_observations=visual_obs,
            contextual_risk_analysis=context_risk,
            reasoning_summary=reasoning,
            farmer_friendly_explanation_en=exp_en,
            farmer_friendly_explanation_hi=exp_hi,
            follow_up_questions=follow_ups,
            expert_review_required=expert_review_required,
            ai_engine=ai_res.get("ai_engine", "Gemini 2.5 Flash"),
            immediate_action=validated_rec.get("immediate_action", ""),
            organic_management=org_mgmt,
            chemical_management=chem_mgmt,
            prevention_steps=prev_steps,
            monitoring_guidance=validated_rec.get("monitoring_guidance", ""),
            area_cost_estimation=cost_estimation,
            created_at=now.isoformat(),
            # Legacy compatibility fields
            cropDetected=detected_crop,
            possibleDisease=detected_disease,
            symptoms=visual_obs,
            recommendedAction=treatment_action
        )

        # 7. Persist to MongoDB
        db_doc = response_data.model_dump()
        db_doc["farmerId"] = farmer_id
        db_doc["filename"] = filename
        db_doc["location"] = {"state": state, "district": district}
        db_doc["growthStage"] = growth_stage
        db_doc["created_at"] = now

        try:
            # Insert into primary crop_analyses collection
            db_manager.crop_analyses.insert_one(db_doc)
            # Also keep disease_analyses updated for legacy queries
            db_manager.disease_analyses.insert_one({
                "analysisId": analysis_id,
                "farmerId": farmer_id,
                "filename": filename,
                "cropDetected": detected_crop,
                "possibleDisease": detected_disease,
                "confidence": display_confidence,
                "severity": severity,
                "symptoms": visual_obs,
                "recommendedAction": treatment_action.model_dump(),
                "created_at": now
            })
        except Exception as e:
            logger.warning(f"Error persisting crop analysis record to MongoDB: {e}")

        # 8. If low confidence, automatically insert into Expert Review Queue
        if expert_review_required:
            try:
                db_manager.expert_reviews.insert_one({
                    "analysisId": analysis_id,
                    "farmerId": farmer_id,
                    "crop": detected_crop,
                    "aiPrediction": detected_disease,
                    "confidence": display_confidence,
                    "severity": severity,
                    "riskLevel": risk_level,
                    "expertStatus": "Pending Review",
                    "expertDiagnosis": None,
                    "expertNotes": "Automatically flagged due to low AI confidence threshold (< 60%) or ambiguous symptoms.",
                    "created_at": now,
                    "updated_at": now
                })
                logger.info(f"Analysis {analysis_id} routed to Expert Review Queue.")
            except Exception as e:
                logger.warning(f"Could not queue expert review: {e}")

        return response_data

    def calculate_area_and_cost(
        self,
        crop: str,
        disease: str,
        area: float,
        unit: str = "Acre"
    ) -> AreaCostCalculationResponse:
        """
        Deterministic Area & Cost Calculator:
        Uses validated recommendation data and deterministic mathematical formulas.
        DOES NOT allow Gemini to invent dosages.
        Conversions:
        - 1 Hectare = 2.471 Acres
        - 1 Bigha = 0.62 Acres
        - 1 Acre = 1.0 Acre
        """
        rec = find_recommendation(crop, disease)
        chem_info = rec.get("chemical_management", {})
        org_info = rec.get("organic_management", {})

        # Use chemical formulation if active, otherwise organic
        mgmt = chem_info if chem_info.get("recommended_rate", 0) > 0 else org_info

        unit_norm = (unit or "Acre").strip().capitalize()
        multiplier = 1.0
        if unit_norm == "Hectare":
            multiplier = 2.471
        elif unit_norm == "Bigha":
            multiplier = 0.62

        std_acres = round(area * multiplier, 2)
        water_per_acre = float(mgmt.get("water_reference_per_acre", 180))
        total_water_liters = round(std_acres * water_per_acre, 1)

        rate = float(mgmt.get("recommended_rate", 2.0))
        rate_unit = mgmt.get("unit", "g/L")
        
        # Calculate total chemical or biological quantity required
        total_quantity = round(total_water_liters * rate, 1)

        # Formatting quantity nicely
        if rate_unit == "g/L":
            if total_quantity >= 1000:
                qty_display = f"{round(total_quantity / 1000.0, 2)} kg"
            else:
                qty_display = f"{int(total_quantity)} grams"
        elif rate_unit == "ml/L":
            if total_quantity >= 1000:
                qty_display = f"{round(total_quantity / 1000.0, 2)} Liters"
            else:
                qty_display = f"{int(total_quantity)} ml"
        else:
            qty_display = f"{round(total_quantity, 1)} {rate_unit}"

        # Estimated cost in INR
        cost_per_acre = float(mgmt.get("estimated_cost_per_acre", 450.0))
        total_cost = round(std_acres * cost_per_acre, 2)

        return AreaCostCalculationResponse(
            crop=rec.get("crop", crop),
            disease=rec.get("disease", disease),
            inputArea=area,
            inputUnit=unit_norm,
            standardAreaAcres=std_acres,
            waterVolumeLiters=total_water_liters,
            managementMethod=mgmt.get("method", "Standard Treatment"),
            productInformation=mgmt.get("product_information", "Standard Formulation"),
            recommendedRate=rate,
            rateUnit=rate_unit,
            requiredQuantityTotal=total_quantity,
            quantityDisplay=qty_display,
            estimatedCostINR=total_cost,
            costDisplay=f"₹{total_cost:,.2f}",
            safetyNotes=mgmt.get("safety_notes", "Wear protective gear during spraying."),
            source=mgmt.get("source", "ICAR / CIBRC Agricultural Guidelines")
        )

    def get_analysis_history(self, farmer_id: str, limit: int = 15) -> List[CropHealthFullResponse]:
        """Fetch chronological diagnosis scans for a farmer."""
        records = list(
            db_manager.crop_analyses.find({"farmerId": farmer_id})
            .sort("created_at", -1)
            .limit(limit)
        )

        results = []
        for r in records:
            r["_id"] = str(r["_id"])
            if isinstance(r.get("created_at"), datetime):
                r["created_at"] = r["created_at"].isoformat()

            crop_name = r.get("crop") or r.get("cropDetected") or "Crop"
            disease_name = r.get("disease_or_pest") or r.get("possibleDisease") or "Condition"
            rec = find_recommendation(crop_name, disease_name)

            r.setdefault("crop", crop_name)
            r.setdefault("disease_or_pest", disease_name)
            r.setdefault("organic_management", rec.get("organic_management", {}))
            r.setdefault("chemical_management", rec.get("chemical_management", {}))
            r.setdefault("prevention_steps", rec.get("prevention_steps", []))
            r.setdefault("monitoring_guidance", rec.get("monitoring_guidance", ""))
            r.setdefault("immediate_action", rec.get("immediate_action", ""))

            # Ensure sub-models parse cleanly
            if r.get("area_cost_estimation") and isinstance(r["area_cost_estimation"], dict):
                r["area_cost_estimation"] = AreaCostCalculationResponse(**r["area_cost_estimation"])
            else:
                r["area_cost_estimation"] = None

            if r.get("recommendedAction") and isinstance(r["recommendedAction"], dict):
                r["recommendedAction"] = TreatmentAction(**r["recommendedAction"])

            results.append(CropHealthFullResponse(**r))

        return results

    def get_analysis_by_id(self, analysis_id: str) -> Optional[CropHealthFullResponse]:
        """Fetch a specific diagnostic report."""
        record = db_manager.crop_analyses.find_one({"analysisId": analysis_id})
        if not record:
            return None
        record["_id"] = str(record["_id"])
        if isinstance(record.get("created_at"), datetime):
            record["created_at"] = record["created_at"].isoformat()

        crop_name = record.get("crop") or record.get("cropDetected") or "Crop"
        disease_name = record.get("disease_or_pest") or record.get("possibleDisease") or "Condition"
        rec = find_recommendation(crop_name, disease_name)

        record.setdefault("crop", crop_name)
        record.setdefault("disease_or_pest", disease_name)
        record.setdefault("organic_management", rec.get("organic_management", {}))
        record.setdefault("chemical_management", rec.get("chemical_management", {}))
        record.setdefault("prevention_steps", rec.get("prevention_steps", []))
        record.setdefault("monitoring_guidance", rec.get("monitoring_guidance", ""))
        record.setdefault("immediate_action", rec.get("immediate_action", ""))

        if record.get("area_cost_estimation") and isinstance(record["area_cost_estimation"], dict):
            record["area_cost_estimation"] = AreaCostCalculationResponse(**record["area_cost_estimation"])
        if record.get("recommendedAction") and isinstance(record["recommendedAction"], dict):
            record["recommendedAction"] = TreatmentAction(**record["recommendedAction"])
        return CropHealthFullResponse(**record)

    def submit_expert_review(self, submission: ExpertReviewSubmission) -> Dict[str, Any]:
        """Agricultural Specialist verifies or corrects an AI prediction."""
        now = datetime.now(timezone.utc)
        status_text = "Verified" if submission.confirmAiPrediction else "Corrected"

        update_doc = {
            "expertStatus": status_text,
            "expertDiagnosis": submission.expertDiagnosis,
            "expertNotes": submission.expertNotes,
            "updated_at": now
        }
        if submission.severity:
            update_doc["severity"] = submission.severity

        result = db_manager.expert_reviews.update_one(
            {"analysisId": submission.analysisId},
            {"$set": update_doc},
            upsert=True
        )

        # Also update in crop_analyses
        db_manager.crop_analyses.update_one(
            {"analysisId": submission.analysisId},
            {
                "$set": {
                    "expert_status": status_text,
                    "expert_diagnosis": submission.expertDiagnosis,
                    "expert_notes": submission.expertNotes,
                    "expert_review_required": False
                }
            }
        )

        return {
            "analysisId": submission.analysisId,
            "status": status_text,
            "updated_at": now.isoformat(),
            "message": f"Specialist review successfully submitted. Diagnosis status updated to '{status_text}'."
        }

    def get_expert_queue(self, limit: int = 20) -> List[ExpertReviewItem]:
        """List analyses pending review by an agricultural pathologist."""
        records = list(
            db_manager.expert_reviews.find({"expertStatus": "Pending Review"})
            .sort("created_at", -1)
            .limit(limit)
        )
        items = []
        for r in records:
            items.append(ExpertReviewItem(
                analysisId=r["analysisId"],
                farmerId=r.get("farmerId"),
                crop=r.get("crop", "Unknown"),
                aiPrediction=r.get("aiPrediction", ""),
                confidence=float(r.get("confidence", 0.0)),
                severity=r.get("severity", "Moderate"),
                riskLevel=r.get("riskLevel", "Moderate"),
                expertStatus=r.get("expertStatus", "Pending Review"),
                expertDiagnosis=r.get("expertDiagnosis"),
                expertNotes=r.get("expertNotes"),
                created_at=r.get("created_at").isoformat() if isinstance(r.get("created_at"), datetime) else str(r.get("created_at", "")),
                updated_at=r.get("updated_at").isoformat() if isinstance(r.get("updated_at"), datetime) else None
            ))
        return items

    def get_regional_risk_report(
        self,
        state: Optional[str] = None,
        district: Optional[str] = None,
        crop: Optional[str] = None
    ) -> RegionalRiskReportResponse:
        """
        Regional Disease Risk Engine:
        Analyzes anonymized, aggregated crop analysis reports in the region
        over the past 30 days to calculate potential outbreak threat level.
        DOES NOT expose farmer personal information.
        """
        filter_q: Dict[str, Any] = {}
        if state:
            filter_q["location.state"] = {"$regex": state, "$options": "i"}
        if district:
            filter_q["location.district"] = {"$regex": district, "$options": "i"}
        if crop:
            filter_q["crop"] = {"$regex": crop, "$options": "i"}

        # Find recent analyses
        recent_cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        filter_q["created_at"] = {"$gte": recent_cutoff}

        reports = list(db_manager.crop_analyses.find(filter_q, {"disease_or_pest": 1, "created_at": 1}))
        total_reports = len(reports)

        # Count frequencies
        counts: Dict[str, int] = {}
        for r in reports:
            p = r.get("disease_or_pest", "Unknown")
            if "healthy" not in p.lower():
                counts[p] = counts.get(p, 0) + 1

        top_pathologies = []
        for path, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:4]:
            pct = round((count / total_reports * 100.0) if total_reports > 0 else 0.0, 1)
            top_pathologies.append(RegionalRiskItem(pathology=path, reportsCount=count, percentage=pct))

        # Risk scoring
        disease_count = sum(counts.values())
        if disease_count >= 20:
            level = "Critical"
            badge = "danger"
            trend = "Rising"
            msg = f"Critical alert: {disease_count} active pathogen reports tracked in {district or 'the region'}. Immediate preventive sprays recommended across farmer clusters."
        elif disease_count >= 10:
            level = "High"
            badge = "warning"
            trend = "Rising"
            msg = f"Early Warning: Elevated reports of {top_pathologies[0].pathology if top_pathologies else 'foliar disease'} detected in {district or 'your district'}."
        elif disease_count >= 4:
            level = "Moderate"
            badge = "info"
            trend = "Stable"
            msg = f"Moderate disease activity. Normal monitoring and prophylactic bio-controls advised."
        else:
            level = "Low"
            badge = "success"
            trend = "Stable"
            msg = f"Low disease pressure reported across {district or state or 'regional'} farmlands. Crops in favorable health."

        advisory = "Follow ICAR integrated pest management guidelines. Keep field borders clear of collateral weeds."

        return RegionalRiskReportResponse(
            state=state or "National",
            district=district or "All Districts",
            crop=crop or "All Crops",
            overallRiskLevel=level,
            riskBadgeColor=badge,
            totalReportsLast30Days=total_reports,
            weeklyTrend=trend,
            topPathologies=top_pathologies,
            earlyWarningMessage=msg,
            advisoryAlert=advisory
        )

crop_health_service = CropHealthService()
# For backward compatibility
disease_ai_service = crop_health_service
