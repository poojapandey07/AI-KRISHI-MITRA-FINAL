"""
End-to-End Automated Test Suite for Gemini AI Crop Health Intelligence & Early Warning System.
Tests multimodal analysis, validated ICAR/CIBRC dosage calculations,
confidence-aware expert review escalation, vernacular guidance, regional risk engine,
and backwards-compatible endpoints.
"""

import sys
import io
import os

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from starlette.testclient import TestClient
from main import app

def run_crop_health_tests():
    print("=" * 60)
    print("RUNNING GEMINI AI CROP HEALTH & REGIONAL RISK ENGINE TEST SUITE")
    print("=" * 60)

    with TestClient(app) as client:
        # 1. Health check
        r_health = client.get("/api/health")
        assert r_health.status_code == 200, f"Health check failed: {r_health.text}"
        print(" [PASS] 1. System health check operational.")

        # 2. Login as Demo Farmer Ramesh Kumar
        r_login = client.post("/api/auth/login", json={
            "mobileOrEmail": "9876543210",
            "password": "Password@123"
        })
        assert r_login.status_code == 200, f"Login failed: {r_login.text}"
        auth_data = r_login.json()["data"]
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f" [PASS] 2. Authenticated as farmer: {auth_data['fullName']} ({auth_data['farmerId']})")

        # 3. Create dummy image bytes for test
        dummy_image = io.BytesIO(b"RIFF....WEBPVP8 ...fake_leaf_image_bytes_for_testing...")
        dummy_image.name = "tomato_early_blight_leaf.jpg"

        # 4. Multimodal Crop Health Analysis (/api/crop/analyze)
        r_analyze = client.post(
            "/api/crop/analyze",
            headers=headers,
            files={"file": ("tomato_leaf.jpg", b"fake_leaf_image_bytes_tomato_blight", "image/jpeg")},
            data={
                "crop": "Tomato",
                "farmArea": "2.5",
                "areaUnit": "Acre",
                "state": "Maharashtra",
                "district": "Nashik",
                "growthStage": "Flowering",
                "symptoms": "Dark brown target rings on bottom foliage after rain"
            }
        )
        assert r_analyze.status_code == 200, f"Analysis failed: {r_analyze.text}"
        res_data = r_analyze.json()["data"]
        analysis_id = res_data["analysisId"]

        assert res_data["crop"] == "Tomato"
        assert "Blight" in res_data["disease_or_pest"]
        assert res_data["confidence"] > 0
        assert len(res_data["visual_observations"]) > 0
        assert res_data["contextual_risk_analysis"] != ""
        assert "farmer_friendly_explanation_en" in res_data
        assert "farmer_friendly_explanation_hi" in res_data
        assert res_data["organic_management"]["product_information"] != ""
        assert res_data["chemical_management"]["product_information"] != ""
        assert res_data["area_cost_estimation"] is not None
        print(f" [PASS] 3. Multimodal Analysis successful: {res_data['crop']} - {res_data['disease_or_pest']} ({res_data['confidence']}% confidence)")
        print(f"        Engine: {res_data['ai_engine']}")
        print(f"        Hindi Guidance: {res_data['farmer_friendly_explanation_hi'][:65]}...")

        # 5. Deterministic Area & Cost Calculator (/api/crop/calculate-cost)
        # Test Acre
        r_calc_acre = client.post("/api/crop/calculate-cost", json={
            "crop": "Tomato",
            "disease": "Early Blight",
            "area": 2.5,
            "unit": "Acre"
        })
        assert r_calc_acre.status_code == 200
        calc_res = r_calc_acre.json()["data"]
        assert calc_res["standardAreaAcres"] == 2.5
        assert calc_res["waterVolumeLiters"] == 450.0  # 2.5 * 180
        assert calc_res["estimatedCostINR"] == 1125.0  # 2.5 * 450
        print(f" [PASS] 4. Deterministic Cost Calculation (2.5 Acres): {calc_res['quantityDisplay']} product, {calc_res['waterVolumeLiters']}L water, {calc_res['costDisplay']}")

        # Test Hectare conversion (1 Hectare = 2.471 Acres)
        r_calc_ha = client.post("/api/crop/calculate-cost", json={
            "crop": "Wheat",
            "disease": "Yellow Rust",
            "area": 1.0,
            "unit": "Hectare"
        })
        assert r_calc_ha.status_code == 200
        ha_res = r_calc_ha.json()["data"]
        assert ha_res["standardAreaAcres"] == 2.47
        print(f" [PASS] 5. Metric Area Conversion (1.0 Hectare -> 2.47 Acres): {ha_res['costDisplay']}")

        # 6. Validated Agricultural Recommendation Lookup (/api/crop/recommendation/{disease})
        r_rec = client.get("/api/crop/recommendation/Early Blight?crop=Tomato")
        assert r_rec.status_code == 200
        rec_data = r_rec.json()["data"]
        assert "Mancozeb" in rec_data["chemical_management"]["product_information"]
        print(f" [PASS] 6. Validated Recommendation retrieved: {rec_data['chemical_management']['product_information']} (Source: {rec_data['chemical_management']['source']})")

        # 7. Regional Disease Risk & Early Warning Engine (/api/crop/risk)
        r_risk = client.get("/api/crop/risk?state=Maharashtra&district=Nashik")
        assert r_risk.status_code == 200
        risk_res = r_risk.json()["data"]
        assert risk_res["district"] == "Nashik"
        assert risk_res["overallRiskLevel"] in ["Low", "Moderate", "High", "Critical"]
        print(f" [PASS] 7. Regional Risk Engine: {risk_res['district']} -> Risk: {risk_res['overallRiskLevel']} ({risk_res['totalReportsLast30Days']} reports, Trend: {risk_res['weeklyTrend']})")
        print(f"        Early Warning: {risk_res['earlyWarningMessage']}")

        # 8. Expert Review Submission (/api/crop/expert-review)
        r_review = client.post("/api/crop/expert-review", json={
            "analysisId": analysis_id,
            "expertDiagnosis": "Confirmed Alternaria solani Early Blight",
            "severity": "Moderate",
            "expertNotes": "Lesions show clear concentric rings. Follow CIBRC protocol.",
            "confirmAiPrediction": True
        })
        assert r_review.status_code == 200
        assert r_review.json()["data"]["status"] == "Verified"
        print(f" [PASS] 8. Specialist Expert Review submitted for {analysis_id}: Status '{r_review.json()['data']['status']}'")

        # 9. Crop Health History (/api/crop/history)
        r_hist = client.get("/api/crop/history", headers=headers)
        assert r_hist.status_code == 200
        history_list = r_hist.json()["data"]
        assert len(history_list) > 0
        assert any(h["analysisId"] == analysis_id for h in history_list)
        print(f" [PASS] 9. Farmer History retrieved: {len(history_list)} diagnosis records.")

        # 10. Backward Compatibility Test (/api/disease-analysis)
        r_legacy = client.post(
            "/api/disease-analysis",
            headers=headers,
            files={"file": ("wheat_rust.jpg", b"fake_leaf_image_bytes_wheat_rust", "image/jpeg")}
        )
        assert r_legacy.status_code == 200
        legacy_data = r_legacy.json()["data"]
        assert "cropDetected" in legacy_data
        assert "possibleDisease" in legacy_data
        print(f" [PASS] 10. Legacy endpoint (/api/disease-analysis) backward compatibility verified: Detected {legacy_data['cropDetected']}.")

    print("=" * 60)
    print(" [SUCCESS] ALL 10 GEMINI CROP HEALTH TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_crop_health_tests()
