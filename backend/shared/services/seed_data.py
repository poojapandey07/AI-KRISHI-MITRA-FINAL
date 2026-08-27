import logging
from datetime import datetime, timezone, timedelta
from config.database import db_manager
from shared.utils.security import hash_password, mask_account_number

logger = logging.getLogger("ai_krishi_mitra.seed")

def seed_initial_data():
    try:
        # 1. Procurement Centres
        centres_count = db_manager.procurement_centres.count_documents({})
        if centres_count == 0:
            centres = [
                {
                    "centreId": "PRC-CTR-101",
                    "name": "Karnal APMC Grain Procurement Hub",
                    "state": "Haryana",
                    "district": "Karnal",
                    "address": "GT Road, Sector 3, Near Anaj Mandi, Karnal - 132001",
                    "availableCrops": ["Wheat", "Paddy (Basmati)", "Mustard", "Maize"],
                    "schedule": "Monday to Saturday, 08:00 AM - 06:00 PM",
                    "dailyCapacityQuintals": 5000,
                    "activeSlots": ["08:00 AM - 10:00 AM", "10:00 AM - 12:00 PM", "12:00 PM - 02:00 PM", "02:00 PM - 04:00 PM", "04:00 PM - 06:00 PM"],
                    "contactPerson": "Shri Rajesh Sharma (Centre Manager)",
                    "contactPhone": "+91 94160 23456",
                    "status": "Operational",
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "centreId": "PRC-CTR-102",
                    "name": "Ludhiana Central FCI Procurement Depot",
                    "state": "Punjab",
                    "district": "Ludhiana",
                    "address": "Ferozepur Road, Grain Market complex, Ludhiana - 141001",
                    "availableCrops": ["Wheat", "Paddy", "Cotton", "Maize"],
                    "schedule": "Monday to Saturday, 08:30 AM - 05:30 PM",
                    "dailyCapacityQuintals": 7500,
                    "activeSlots": ["08:30 AM - 10:30 AM", "10:30 AM - 12:30 PM", "01:30 PM - 03:30 PM", "03:30 PM - 05:30 PM"],
                    "contactPerson": "Sardar Gurpreet Singh",
                    "contactPhone": "+91 98140 76543",
                    "status": "Operational",
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "centreId": "PRC-CTR-103",
                    "name": "Nashik Kisan Mandi & Cold Chain Centre",
                    "state": "Maharashtra",
                    "district": "Nashik",
                    "address": "Dindori Road, APMC Yard, Nashik - 422004",
                    "availableCrops": ["Onion", "Tomato", "Soyabean", "Wheat", "Grapes"],
                    "schedule": "All Days, 07:00 AM - 07:00 PM",
                    "dailyCapacityQuintals": 6000,
                    "activeSlots": ["07:00 AM - 09:00 AM", "09:00 AM - 11:00 AM", "11:00 AM - 01:00 PM", "02:00 PM - 04:00 PM", "04:00 PM - 06:00 PM"],
                    "contactPerson": "Shri Nitin Patil",
                    "contactPhone": "+91 98220 98765",
                    "status": "Operational",
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "centreId": "PRC-CTR-104",
                    "name": "Indore Malwa Krishi Mandi Centre",
                    "state": "Madhya Pradesh",
                    "district": "Indore",
                    "address": "Chhavani Mandi Complex, Indore - 452001",
                    "availableCrops": ["Soyabean", "Wheat", "Chana (Chickpea)", "Garlic"],
                    "schedule": "Monday to Saturday, 09:00 AM - 06:00 PM",
                    "dailyCapacityQuintals": 8000,
                    "activeSlots": ["09:00 AM - 11:00 AM", "11:00 AM - 01:00 PM", "02:00 PM - 04:00 PM", "04:00 PM - 06:00 PM"],
                    "contactPerson": "Shri Anand Verma",
                    "contactPhone": "+91 94250 11223",
                    "status": "Operational",
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "centreId": "PRC-CTR-105",
                    "name": "Rajkot APMC Saurashtra Hub",
                    "state": "Gujarat",
                    "district": "Rajkot",
                    "address": "Bedi Yard, National Highway 8B, Rajkot - 360003",
                    "availableCrops": ["Cotton", "Groundnut", "Mustard", "Wheat", "Cumin"],
                    "schedule": "Monday to Saturday, 08:00 AM - 05:00 PM",
                    "dailyCapacityQuintals": 6500,
                    "activeSlots": ["08:00 AM - 10:00 AM", "10:00 AM - 12:00 PM", "01:00 PM - 03:00 PM", "03:00 PM - 05:00 PM"],
                    "contactPerson": "Shri Bhavesh Patel",
                    "contactPhone": "+91 97270 44556",
                    "status": "Operational",
                    "created_at": datetime.now(timezone.utc)
                }
            ]
            db_manager.procurement_centres.insert_many(centres)
            logger.info("Seeded procurement centres successfully.")

        # 2. Market Live Prices
        prices_count = db_manager.market_prices.count_documents({})
        if prices_count == 0:
            prices = [
                {
                    "crop": "Wheat",
                    "variety": "Sharbati / PBW 550",
                    "mandi": "Karnal APMC Yard",
                    "district": "Karnal",
                    "state": "Haryana",
                    "modalPrice": 2425,
                    "minPrice": 2350,
                    "maxPrice": 2550,
                    "unit": "₹ / Quintal",
                    "msp": 2275,
                    "trend": "up",
                    "change": "+₹45",
                    "arrivalVolumeQuintals": 3200,
                    "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
                },
                {
                    "crop": "Paddy (Basmati)",
                    "variety": "Pusa 1121",
                    "mandi": "Taraori Mandi",
                    "district": "Karnal",
                    "state": "Haryana",
                    "modalPrice": 3850,
                    "minPrice": 3600,
                    "maxPrice": 4100,
                    "unit": "₹ / Quintal",
                    "msp": 2203,
                    "trend": "up",
                    "change": "+₹80",
                    "arrivalVolumeQuintals": 1850,
                    "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
                },
                {
                    "crop": "Mustard",
                    "variety": "Pusa Bold / PM 30",
                    "mandi": "Hisar Grain Market",
                    "district": "Hisar",
                    "state": "Haryana",
                    "modalPrice": 5650,
                    "minPrice": 5400,
                    "maxPrice": 5850,
                    "unit": "₹ / Quintal",
                    "msp": 5650,
                    "trend": "flat",
                    "change": "₹0",
                    "arrivalVolumeQuintals": 1200,
                    "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
                },
                {
                    "crop": "Cotton",
                    "variety": "Bt Cotton Medium Staple",
                    "mandi": "Sirsa Mandi",
                    "district": "Sirsa",
                    "state": "Haryana",
                    "modalPrice": 7200,
                    "minPrice": 6900,
                    "maxPrice": 7450,
                    "unit": "₹ / Quintal",
                    "msp": 7020,
                    "trend": "down",
                    "change": "-₹60",
                    "arrivalVolumeQuintals": 950,
                    "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
                },
                {
                    "crop": "Soyabean",
                    "variety": "JS 335 / Yellow",
                    "mandi": "Indore Main Mandi",
                    "district": "Indore",
                    "state": "Madhya Pradesh",
                    "modalPrice": 4650,
                    "minPrice": 4450,
                    "maxPrice": 4850,
                    "unit": "₹ / Quintal",
                    "msp": 4600,
                    "trend": "up",
                    "change": "+₹35",
                    "arrivalVolumeQuintals": 4100,
                    "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
                },
                {
                    "crop": "Chana (Chickpea)",
                    "variety": "Desi Bold",
                    "mandi": "Bhopal Karond Mandi",
                    "district": "Bhopal",
                    "state": "Madhya Pradesh",
                    "modalPrice": 5800,
                    "minPrice": 5600,
                    "maxPrice": 6050,
                    "unit": "₹ / Quintal",
                    "msp": 5440,
                    "trend": "up",
                    "change": "+₹50",
                    "arrivalVolumeQuintals": 1400,
                    "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
                },
                {
                    "crop": "Maize",
                    "variety": "Hybrid Yellow",
                    "mandi": "Khanna Mandi",
                    "district": "Ludhiana",
                    "state": "Punjab",
                    "modalPrice": 2150,
                    "minPrice": 2000,
                    "maxPrice": 2250,
                    "unit": "₹ / Quintal",
                    "msp": 2090,
                    "trend": "down",
                    "change": "-₹25",
                    "arrivalVolumeQuintals": 800,
                    "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
                },
                {
                    "crop": "Tomato",
                    "variety": "Hybrid Red",
                    "mandi": "Nashik APMC",
                    "district": "Nashik",
                    "state": "Maharashtra",
                    "modalPrice": 1800,
                    "minPrice": 1500,
                    "maxPrice": 2200,
                    "unit": "₹ / Quintal",
                    "msp": None,
                    "trend": "up",
                    "change": "+₹150",
                    "arrivalVolumeQuintals": 2600,
                    "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
                },
                {
                    "crop": "Onion",
                    "variety": "Red Nashik Quality",
                    "mandi": "Lasalgaon APMC",
                    "district": "Nashik",
                    "state": "Maharashtra",
                    "modalPrice": 2350,
                    "minPrice": 1900,
                    "maxPrice": 2650,
                    "unit": "₹ / Quintal",
                    "msp": None,
                    "trend": "down",
                    "change": "-₹90",
                    "arrivalVolumeQuintals": 5400,
                    "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
                }
            ]
            db_manager.market_prices.insert_many(prices)
            logger.info("Seeded market prices successfully.")

        # 3. Institutional Buyer Opportunities
        buyers_count = db_manager.buyers.count_documents({})
        if buyers_count == 0:
            buyers = [
                {
                    "buyerId": "BYR-701",
                    "companyName": "ITC Agri Business Division (e-Choupal)",
                    "category": "Corporate Processor",
                    "cropRequirement": "Wheat",
                    "preferredVariety": "Sharbati & Lokwan High Gluten",
                    "requiredQuantity": "500 MT (5000 Quintals)",
                    "indicativePrice": 2520,
                    "unit": "₹ / Quintal",
                    "location": "Karnal & Kurukshetra Procurement Points, Haryana",
                    "qualitySpecifications": "Moisture < 12%, Foreign Matter < 0.75%, No Weeviled Grains",
                    "paymentTerms": "Direct Bank Transfer within 48 hours of QC pass",
                    "status": "Urgent",
                    "contactEmail": "sourcing.north@itcagri.com",
                    "contactPhone": "+91 1800 200 4567",
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "buyerId": "BYR-702",
                    "companyName": "Patanjali Foods Limited",
                    "category": "Agro FMCG",
                    "cropRequirement": "Mustard",
                    "preferredVariety": "High Oil Content (> 40%)",
                    "requiredQuantity": "350 MT",
                    "indicativePrice": 5780,
                    "unit": "₹ / Quintal",
                    "location": "Hisar & Rewari Depots, Haryana",
                    "qualitySpecifications": "Clean, dried, oil content test on delivery",
                    "paymentTerms": "T+1 Day Direct Credit into verified bank account",
                    "status": "Accepting Bids",
                    "contactEmail": "procurement@patanjalifoods.com",
                    "contactPhone": "+91 1800 180 4108",
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "buyerId": "BYR-703",
                    "companyName": "BigBasket Farm Fresh Sourcing",
                    "category": "Modern Retail",
                    "cropRequirement": "Tomato & Onion",
                    "preferredVariety": "Grade A Table Produce",
                    "requiredQuantity": "100 MT Weekly",
                    "indicativePrice": 2100,
                    "unit": "₹ / Quintal",
                    "location": "Nashik Collection Center, Maharashtra",
                    "qualitySpecifications": "Firm, uniform size, zero chemical residue threshold",
                    "paymentTerms": "Weekly consolidated direct credit",
                    "status": "Open",
                    "contactEmail": "farmer.connect@bigbasket.com",
                    "contactPhone": "+91 80 4000 7000",
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "buyerId": "BYR-704",
                    "companyName": "Cargill India Agriculture Supply Chain",
                    "category": "MNC Grain Exporter",
                    "cropRequirement": "Maize & Soyabean",
                    "preferredVariety": "Yellow Feed Grade & Food Grade Non-GMO",
                    "requiredQuantity": "1000 MT",
                    "indicativePrice": 2280,
                    "unit": "₹ / Quintal",
                    "location": "Indore Malwa Logistics Hub, Madhya Pradesh",
                    "qualitySpecifications": "Moisture <= 14%, Aflatoxin < 20 ppb",
                    "paymentTerms": "24 hours direct NEFT/RTGS after weighing",
                    "status": "Open",
                    "contactEmail": "india_grain_sourcing@cargill.com",
                    "contactPhone": "+91 124 409 0000",
                    "created_at": datetime.now(timezone.utc)
                }
            ]
            db_manager.buyers.insert_many(buyers)
            logger.info("Seeded buyer listings successfully.")

        # 4. Demo Farmer Account
        demo_farmer = db_manager.farmers.find_one({"mobile": "9876543210"})
        if not demo_farmer:
            farmer_id = "FMR-88012"
            now = datetime.now(timezone.utc)
            farmer_doc = {
                "farmerId": farmer_id,
                "fullName": "Ramesh Kumar",
                "mobile": "9876543210",
                "email": "ramesh.kumar@example.com",
                "hashedPassword": hash_password("Password@123"),
                "state": "Haryana",
                "district": "Karnal",
                "village": "Nilokheri",
                "created_at": now,
                "updated_at": now
            }
            db_manager.farmers.insert_one(farmer_doc)

            # Pre-seed Land
            db_manager.land_records.insert_one({
                "landId": "LND-1001",
                "farmerId": farmer_id,
                "area": 4.5,
                "unit": "Acres",
                "soilType": "Alluvial Soil (Loamy)",
                "irrigationType": "Tube-well with Drip System",
                "location": "Khasra No. 142/3, Nilokheri, Karnal",
                "created_at": now
            })

            # Pre-seed Crops
            crop_id_1 = "CRP-2001"
            crop_id_2 = "CRP-2002"
            db_manager.crops.insert_many([
                {
                    "cropId": crop_id_1,
                    "farmerId": farmer_id,
                    "cropName": "Wheat",
                    "variety": "HD-2967 (High Yielding)",
                    "sowingDate": (now - timedelta(days=90)).strftime("%Y-%m-%d"),
                    "expectedHarvest": (now + timedelta(days=25)).strftime("%Y-%m-%d"),
                    "cultivatedArea": 3.0,
                    "areaUnit": "Acres",
                    "estimatedYieldQuintals": 65.0,
                    "created_at": now
                },
                {
                    "cropId": crop_id_2,
                    "farmerId": farmer_id,
                    "cropName": "Mustard",
                    "variety": "Pusa Bold",
                    "sowingDate": (now - timedelta(days=105)).strftime("%Y-%m-%d"),
                    "expectedHarvest": (now + timedelta(days=10)).strftime("%Y-%m-%d"),
                    "cultivatedArea": 1.5,
                    "areaUnit": "Acres",
                    "estimatedYieldQuintals": 18.0,
                    "created_at": now
                }
            ])

            # Pre-seed Verified Bank Account
            raw_acc = "50100234891234"
            db_manager.bank_accounts.insert_one({
                "bankAccountId": "BNK-5012",
                "farmerId": farmer_id,
                "bankName": "State Bank of India",
                "accountHolder": "Ramesh Kumar",
                "accountNumber": raw_acc,
                "maskedAccountNumber": mask_account_number(raw_acc),
                "ifscCode": "SBIN0001234",
                "branchName": "Nilokheri Main Branch",
                "verificationStatus": "Verified",
                "verifiedAt": now.isoformat(),
                "created_at": now
            })

            # Pre-seed a Procurement Application
            app_id = "APP-44210"
            prc_id = "PRC-00124"
            pay_id = "PAY-00891"
            db_manager.procurement_applications.insert_one({
                "applicationId": app_id,
                "procurementId": prc_id,
                "farmerId": farmer_id,
                "centreId": "PRC-CTR-101",
                "centreName": "Karnal APMC Grain Procurement Hub",
                "cropId": crop_id_1,
                "cropName": "Wheat",
                "variety": "HD-2967 (High Yielding)",
                "quantityQuintals": 30.0,
                "bookingDate": now.strftime("%Y-%m-%d"),
                "timeSlot": "10:00 AM - 12:00 PM",
                "tokenNumber": "TKN-042",
                "queuePosition": 3,
                "estimatedWaitMinutes": 35,
                "status": "Payment Initiated",
                "qualityGrade": "Grade A (FAQ Passed)",
                "moisturePercent": 11.4,
                "created_at": now
            })

            # Pre-seed Payment linked to Procurement
            db_manager.payments.insert_one({
                "paymentId": pay_id,
                "procurementId": prc_id,
                "applicationId": app_id,
                "farmerId": farmer_id,
                "crop": "Wheat",
                "quantityQuintals": 30.0,
                "ratePerQuintal": 2425.0,
                "amount": 72750.0,
                "bankAccountId": "BNK-5012",
                "bankName": "State Bank of India",
                "maskedAccountNumber": mask_account_number(raw_acc),
                "status": "Payment Initiated",
                "initiatedAt": now.isoformat(),
                "creditedAt": None,
                "remarks": "Procurement settlement for 30 Quintals Wheat Grade A at Karnal APMC Hub",
                "created_at": now
            })

            logger.info("Seeded demo farmer Ramesh Kumar (9876543210) successfully.")

    except Exception as e:
        logger.error(f"Error during data seeding: {e}")
