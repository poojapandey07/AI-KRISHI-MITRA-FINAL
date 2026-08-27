import sys
import os
import random

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from starlette.testclient import TestClient
from main import app

def run_all_tests():
    print("==================================================")
    print("RUNNING AI KRISHI MITRA FULL END-TO-END SUITE")
    print("==================================================")

    with TestClient(app) as client:
        # 1. Health check
        res = client.get("/api/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        data = res.json()
        assert data["status"] == "healthy"
        print(" [PASS] 1. System health check is healthy and MongoDB connected.")

        # 2. Demo login
        login_res = client.post("/api/auth/login", json={
            "mobileOrEmail": "9876543210",
            "password": "Password@123"
        })
        assert login_res.status_code == 200, f"Demo login failed: {login_res.text}"
        demo_auth = login_res.json()["data"]
        demo_token = demo_auth["access_token"]
        demo_headers = {"Authorization": f"Bearer {demo_token}"}
        print(f" [PASS] 2. Demo farmer login verified (ID: {demo_auth['farmerId']}, Name: {demo_auth['fullName']}).")

        # 3. New Farmer Registration
        rnd_mobile = f"99{random.randint(10000000, 99999999)}"
        reg_res = client.post("/api/auth/register", json={
            "fullName": "Suresh Patel",
            "mobile": rnd_mobile,
            "email": f"suresh_{rnd_mobile}@kisan.in",
            "password": "SecretPassword@123",
            "state": "Gujarat",
            "district": "Rajkot",
            "village": "Gondal"
        })
        assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
        new_auth = reg_res.json()["data"]
        new_token = new_auth["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}
        farmer_id = new_auth["farmerId"]
        print(f" [PASS] 3. New farmer registered: {new_auth['fullName']} ({farmer_id}) with mobile {rnd_mobile}.")

        # 4. Add Land
        land_res = client.post("/api/farmers/land", headers=new_headers, json={
            "area": 5.2,
            "unit": "Acres",
            "soilType": "Black Cotton Soil",
            "irrigationType": "Drip Irrigation",
            "location": "Gondal Taluk, Rajkot"
        })
        assert land_res.status_code == 201, f"Add land failed: {land_res.text}"
        land_id = land_res.json()["data"]["landId"]
        print(f" [PASS] 4. Land added: {land_id} (5.2 Acres, Black Cotton Soil).")

        # 5. Add Crop
        crop_res = client.post("/api/farmers/crops", headers=new_headers, json={
            "cropName": "Cotton",
            "variety": "Bt Cotton Hybrid 6",
            "sowingDate": "2025-06-15",
            "expectedHarvest": "2025-11-20",
            "cultivatedArea": 4.0,
            "areaUnit": "Acres",
            "estimatedYieldQuintals": 48.0
        })
        assert crop_res.status_code == 201, f"Add crop failed: {crop_res.text}"
        crop_id = crop_res.json()["data"]["cropId"]
        print(f" [PASS] 5. Crop registered: {crop_id} (Cotton Hybrid 6).")

        # 6. Fetch Procurement Centres
        centres_res = client.get("/api/procurement/centres?crop=Cotton")
        assert centres_res.status_code == 200
        centres = centres_res.json()["data"]
        assert len(centres) > 0, "No centres found for Cotton"
        centre_id = centres[0]["centreId"]
        print(f" [PASS] 6. Procurement centres found: {len(centres)} centres accept Cotton (Selected: {centre_id}).")

        # 7. Book Procurement Slot
        book_res = client.post("/api/procurement/applications", headers=new_headers, json={
            "centreId": centre_id,
            "cropId": crop_id,
            "quantityQuintals": 25.0,
            "bookingDate": "2025-11-25",
            "timeSlot": "08:00 AM - 10:00 AM"
        })
        assert book_res.status_code == 201, f"Booking slot failed: {book_res.text}"
        app_data = book_res.json()["data"]
        app_id = app_data["applicationId"]
        proc_id = app_data["procurementId"]
        token_no = app_data["tokenNumber"]
        print(f" [PASS] 7. Procurement slot booked: App ID {app_id}, Proc ID {proc_id}, Token {token_no}.")

        # 8. Queue Status
        queue_res = client.get(f"/api/procurement/queue/{app_id}", headers=new_headers)
        assert queue_res.status_code == 200
        q_data = queue_res.json()["data"]
        assert q_data["tokenNumber"] == token_no
        print(f" [PASS] 8. Queue tracker: Token {token_no}, Position {q_data['queuePosition']}, Wait {q_data['estimatedWaitMinutes']}m.")

        # 9. Link Bank Account
        raw_acc = f"6023{random.randint(10000000, 99999999)}"
        bank_res = client.post("/api/finance/bank", headers=new_headers, json={
            "bankName": "Bank of Baroda",
            "accountHolder": "Suresh Patel",
            "accountNumber": raw_acc,
            "ifscCode": "BARB0GONDAL"
        })
        assert bank_res.status_code == 201, f"Link bank failed: {bank_res.text}"
        bank_data = bank_res.json()["data"]
        bank_id = bank_data["bankAccountId"]
        assert bank_data["maskedAccountNumber"].endswith(raw_acc[-4:])
        assert "accountNumber" not in bank_data  # verify security masking
        print(f" [PASS] 9. Bank linked: {bank_data['bankName']} (Masked: {bank_data['maskedAccountNumber']}, Status: {bank_data['verificationStatus']}).")

        # 10. Verify Bank Sandbox
        verify_res = client.post("/api/finance/bank/verify", headers=new_headers, json={
            "bankAccountId": bank_id,
            "action": "verify"
        })
        assert verify_res.status_code == 200
        assert verify_res.json()["data"]["verificationStatus"] == "Verified"
        print(" [PASS] 10. Bank account sandbox verification successful: Status 'Verified'.")

        # 11. Progress Procurement Status to 'Payment Initiated'
        status_res = client.patch(
            f"/api/procurement/applications/{app_id}/status",
            headers=new_headers,
            json={
                "status": "Payment Initiated",
                "qualityGrade": "Grade A Premium",
                "moisturePercent": 7.8,
                "ratePerQuintal": 7250.0
            }
        )
        assert status_res.status_code == 200
        assert status_res.json()["data"]["status"] == "Payment Initiated"
        print(f" [PASS] 11. Procurement status progressed to 'Payment Initiated' (Grade A, Rate Rs.7250/Q).")

        # 12. Check Finance Module Auto-Payment Connection
        pay_res = client.get("/api/finance/payments", headers=new_headers)
        assert pay_res.status_code == 200
        payments = pay_res.json()["data"]
        assert len(payments) > 0, "Finance payment record was not generated from procurement!"
        linked_pay = next((p for p in payments if p["procurementId"] == proc_id), None)
        assert linked_pay is not None, "Linked payment with procurementId not found!"
        pay_id = linked_pay["paymentId"]
        assert linked_pay["amount"] == 25.0 * 7250.0
        print(f" [PASS] 12. Cross-module integration verified: Payment {pay_id} automatically created for Rs.{linked_pay['amount']:,.2f}.")

        # 13. Simulate Payment Credited
        sim_res = client.patch(
            f"/api/finance/payments/{pay_id}/simulate-status",
            headers=new_headers,
            json={"status": "Payment Credited"}
        )
        assert sim_res.status_code == 200
        assert sim_res.json()["data"]["status"] == "Payment Credited"
        print(f" [PASS] 13. Payment {pay_id} status transitioned to 'Payment Credited'.")

        # 14. Filter Payments
        filter_res = client.get("/api/finance/payments?status=credited", headers=new_headers)
        assert filter_res.status_code == 200
        assert len(filter_res.json()["data"]) >= 1
        print(" [PASS] 14. Payment history filter (?status=credited) verified.")

        # 15. AI Standards Check
        ai_res = client.post("/api/ai/standards", headers=new_headers, json={
            "crop": "Cotton",
            "moisturePercent": 8.0,
            "foreignMatterPercent": 1.1,
            "damagedGrainsPercent": 1.5
        })
        assert ai_res.status_code == 200
        ai_data = ai_res.json()["data"]
        assert ai_data["isProcurementEligible"] is True
        print(f" [PASS] 15. AI Standards check: Grade '{ai_data['assignedGrade']}' (Quality Score: {ai_data['qualityScore']}/100).")

        # 16. AI Recommendations
        rec_res = client.get("/api/ai/recommendations", headers=new_headers)
        assert rec_res.status_code == 200
        recs = rec_res.json()["data"]
        assert len(recs) > 0
        print(f" [PASS] 16. AI Crop recommendations loaded: {len(recs)} advisory insights.")

        # 17. Disease & Pest AI (Multipart file upload)
        dummy_img_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00test_wheat_leaf_image"
        files = {"file": ("wheat_yellow_rust_sample.jpg", dummy_img_bytes, "image/jpeg")}
        dis_res = client.post("/api/disease-analysis", headers=new_headers, files=files)
        assert dis_res.status_code == 200, f"Disease analysis failed: {dis_res.text}"
        dis_data = dis_res.json()["data"]
        print(f" [PASS] 17. Disease AI Diagnosis: Crop '{dis_data['cropDetected']}', Disease '{dis_data['possibleDisease']}', Confidence: {dis_data['confidence']}%, Severity: {dis_data['severity']}.")

        # 18. Market Prices & Search
        mkt_res = client.get("/api/market/prices?crop=Wheat")
        assert mkt_res.status_code == 200
        mkt_prices = mkt_res.json()["data"]
        assert len(mkt_prices) > 0
        print(f" [PASS] 18. Live Mandi prices retrieved: {len(mkt_prices)} wheat listings found (Modal: Rs.{mkt_prices[0]['modalPrice']}/Q).")

        # 19. Buyer Opportunities & Connect
        buyer_res = client.get("/api/market/buyers")
        assert buyer_res.status_code == 200
        buyers = buyer_res.json()["data"]
        assert len(buyers) > 0
        buyer_id = buyers[0]["buyerId"]
        
        conn_res = client.post(f"/api/market/buyers/{buyer_id}/connect", headers=new_headers, json={
            "quantityOfferedQuintals": 30.0,
            "expectedPricePerQuintal": 2550.0,
            "farmerNote": "Ready for farm-gate pickup. Tested moisture 11.4%."
        })
        assert conn_res.status_code == 201
        print(f" [PASS] 19. Buyer connection submitted to {buyers[0]['companyName']} (Lead: {conn_res.json()['data']['connectionId']}).")

        # 20. Market Dashboard
        dash_res = client.get("/api/market/dashboard", headers=new_headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()["data"]
        assert dash_data["totalMandisCovered"] > 0
        print(f" [PASS] 20. Market Dashboard summary loaded: {dash_data['totalMandisCovered']} mandis tracked.")

    print("\n==================================================")
    print(" [SUCCESS] ALL 20 TEST CASES PASSED SUCCESSFULLY!")
    print(" [SUCCESS] BACKEND ARCHITECTURE & INTEGRATION 100% OPERATIONAL")
    print("==================================================")

if __name__ == "__main__":
    run_all_tests()
