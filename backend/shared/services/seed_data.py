import logging
from datetime import datetime, timezone, timedelta
from config.database import db_manager
from shared.utils.security import hash_password, mask_account_number

logger = logging.getLogger("ai_krishi_mitra.seed")

def seed_initial_data():
    try:
        now = datetime.now(timezone.utc)

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
                    "created_at": now
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
                    "created_at": now
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
                    "created_at": now
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
                    "created_at": now
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
                    "created_at": now
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
                    "lastUpdated": now.strftime("%Y-%m-%d %H:%M")
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
                    "lastUpdated": now.strftime("%Y-%m-%d %H:%M")
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
                    "lastUpdated": now.strftime("%Y-%m-%d %H:%M")
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
                    "lastUpdated": now.strftime("%Y-%m-%d %H:%M")
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
                    "lastUpdated": now.strftime("%Y-%m-%d %H:%M")
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
                    "lastUpdated": now.strftime("%Y-%m-%d %H:%M")
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
                    "lastUpdated": now.strftime("%Y-%m-%d %H:%M")
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
                    "lastUpdated": now.strftime("%Y-%m-%d %H:%M")
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
                    "lastUpdated": now.strftime("%Y-%m-%d %H:%M")
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
                    "created_at": now
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
                    "created_at": now
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
                    "created_at": now
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
                    "created_at": now
                }
            ]
            db_manager.buyers.insert_many(buyers)
            logger.info("Seeded buyer listings successfully.")

        # 4. PRE-SEED 6 REAL DEMO FARMER ACCOUNTS (For the 6 team members)
        demo_accounts = [
            {
                "farmerId": "FMR-88012",
                "fullName": "Ramesh Kumar",
                "mobile": "9876543210",
                "email": "ramesh.kumar@example.com",
                "password": "Password@123",
                "state": "Haryana",
                "district": "Karnal",
                "village": "Nilokheri",
                "land": {
                    "landId": "LND-1001",
                    "area": 4.5,
                    "unit": "Acres",
                    "soilType": "Alluvial Soil (Loamy)",
                    "irrigationType": "Tube-well with Drip System",
                    "location": "Khasra No. 142/3, Nilokheri, Karnal"
                },
                "crops": [
                    {"cropId": "CRP-2001", "cropName": "Wheat", "variety": "HD-2967", "sowing": 90, "harvest": 25, "area": 3.0, "yield": 65.0},
                    {"cropId": "CRP-2002", "cropName": "Mustard", "variety": "Pusa Bold", "sowing": 105, "harvest": 10, "area": 1.5, "yield": 18.0}
                ],
                "bank": {
                    "bankAccountId": "BNK-5012",
                    "bankName": "State Bank of India",
                    "accountNumber": "50100234891234",
                    "ifscCode": "SBIN0001234",
                    "branch": "Nilokheri Main Branch",
                    "status": "Verified"
                },
                "procurement": {
                    "applicationId": "APP-44210",
                    "procurementId": "PRC-00124",
                    "centreId": "PRC-CTR-101",
                    "centreName": "Karnal APMC Grain Procurement Hub",
                    "cropId": "CRP-2001",
                    "cropName": "Wheat",
                    "variety": "HD-2967",
                    "qty": 30.0,
                    "slot": "10:00 AM - 12:00 PM",
                    "token": "TKN-042",
                    "queue": 3,
                    "wait": 35,
                    "status": "Payment Initiated",
                    "amount": 72750.0
                },
                "payment": {
                    "paymentId": "PAY-00891",
                    "amount": 72750.0,
                    "status": "Payment Initiated",
                    "remarks": "Procurement settlement for 30 Quintals Wheat Grade A at Karnal APMC Hub"
                }
            },
            {
                "farmerId": "FMR-88013",
                "fullName": "Gurpreet Singh",
                "mobile": "9876543211",
                "email": "gurpreet.singh@example.com",
                "password": "Password@123",
                "state": "Punjab",
                "district": "Ludhiana",
                "village": "Khanna",
                "land": {
                    "landId": "LND-1002",
                    "area": 8.0,
                    "unit": "Acres",
                    "soilType": "Alluvial Loam",
                    "irrigationType": "Canal Water Feed",
                    "location": "GT Road, Khanna Kalan, Ludhiana"
                },
                "crops": [
                    {"cropId": "CRP-2003", "cropName": "Wheat", "variety": "PBW-550", "sowing": 95, "harvest": 20, "area": 5.0, "yield": 110.0},
                    {"cropId": "CRP-2004", "cropName": "Maize", "variety": "Hybrid Yellow", "sowing": 110, "harvest": 15, "area": 3.0, "yield": 55.0}
                ],
                "bank": {
                    "bankAccountId": "BNK-5013",
                    "bankName": "Punjab National Bank",
                    "accountNumber": "0123002100876543",
                    "ifscCode": "PUNB0012300",
                    "branch": "Khanna Mandi Branch",
                    "status": "Verified"
                },
                "procurement": {
                    "applicationId": "APP-44211",
                    "procurementId": "PRC-00125",
                    "centreId": "PRC-CTR-102",
                    "centreName": "Ludhiana Central FCI Procurement Depot",
                    "cropId": "CRP-2003",
                    "cropName": "Wheat",
                    "variety": "PBW-550",
                    "qty": 50.0,
                    "slot": "08:30 AM - 10:30 AM",
                    "token": "TKN-018",
                    "queue": 2,
                    "wait": 20,
                    "status": "Slot Confirmed",
                    "amount": 121250.0
                },
                "payment": None
            },
            {
                "farmerId": "FMR-88014",
                "fullName": "Suresh Patel",
                "mobile": "9876543212",
                "email": "suresh.patel@example.com",
                "password": "Password@123",
                "state": "Gujarat",
                "district": "Rajkot",
                "village": "Gondal",
                "land": {
                    "landId": "LND-1003",
                    "area": 5.5,
                    "unit": "Acres",
                    "soilType": "Black Cotton Soil",
                    "irrigationType": "Drip Irrigation",
                    "location": "Survey 88, Gondal Rural, Rajkot"
                },
                "crops": [
                    {"cropId": "CRP-2005", "cropName": "Cotton", "variety": "Bt Cotton 6", "sowing": 120, "harvest": 10, "area": 3.5, "yield": 42.0},
                    {"cropId": "CRP-2006", "cropName": "Mustard", "variety": "Pusa Bold", "sowing": 80, "harvest": 30, "area": 2.0, "yield": 24.0}
                ],
                "bank": {
                    "bankAccountId": "BNK-5014",
                    "bankName": "Bank of Baroda",
                    "accountNumber": "04560100098765",
                    "ifscCode": "BARB0GONDAL",
                    "branch": "Gondal Main Branch",
                    "status": "Verified"
                },
                "procurement": {
                    "applicationId": "APP-44212",
                    "procurementId": "PRC-00126",
                    "centreId": "PRC-CTR-105",
                    "centreName": "Rajkot APMC Saurashtra Hub",
                    "cropId": "CRP-2005",
                    "cropName": "Cotton",
                    "variety": "Bt Cotton 6",
                    "qty": 25.0,
                    "slot": "08:00 AM - 10:00 AM",
                    "token": "TKN-005",
                    "queue": 0,
                    "wait": 0,
                    "status": "Procurement Accepted",
                    "amount": 180000.0
                },
                "payment": {
                    "paymentId": "PAY-00892",
                    "amount": 180000.0,
                    "status": "Payment Credited",
                    "remarks": "DBT Direct Bank Credit for 25 Quintals Bt Cotton Grade A"
                }
            },
            {
                "farmerId": "FMR-88015",
                "fullName": "Nitin Patil",
                "mobile": "9876543213",
                "email": "nitin.patil@example.com",
                "password": "Password@123",
                "state": "Maharashtra",
                "district": "Nashik",
                "village": "Dindori",
                "land": {
                    "landId": "LND-1004",
                    "area": 6.0,
                    "unit": "Acres",
                    "soilType": "Loamy Clay Soil",
                    "irrigationType": "Sprinkler System",
                    "location": "Gat No. 204, Dindori Taluka, Nashik"
                },
                "crops": [
                    {"cropId": "CRP-2007", "cropName": "Tomato", "variety": "Hybrid Red", "sowing": 60, "harvest": 15, "area": 3.0, "yield": 90.0},
                    {"cropId": "CRP-2008", "cropName": "Onion", "variety": "Red Nashik", "sowing": 75, "harvest": 20, "area": 3.0, "yield": 80.0}
                ],
                "bank": {
                    "bankAccountId": "BNK-5015",
                    "bankName": "HDFC Bank",
                    "accountNumber": "50100456789012",
                    "ifscCode": "HDFC0000123",
                    "branch": "Nashik City Branch",
                    "status": "Verified"
                },
                "procurement": {
                    "applicationId": "APP-44213",
                    "procurementId": "PRC-00127",
                    "centreId": "PRC-CTR-103",
                    "centreName": "Nashik Kisan Mandi & Cold Chain Centre",
                    "cropId": "CRP-2008",
                    "cropName": "Onion",
                    "variety": "Red Nashik",
                    "qty": 40.0,
                    "slot": "09:00 AM - 11:00 AM",
                    "token": "TKN-031",
                    "queue": 1,
                    "wait": 15,
                    "status": "Quality Checked",
                    "amount": 94000.0
                },
                "payment": None
            },
            {
                "farmerId": "FMR-88016",
                "fullName": "Anand Verma",
                "mobile": "9876543214",
                "email": "anand.verma@example.com",
                "password": "Password@123",
                "state": "Madhya Pradesh",
                "district": "Indore",
                "village": "Sanwer",
                "land": {
                    "landId": "LND-1005",
                    "area": 7.2,
                    "unit": "Acres",
                    "soilType": "Deep Black Malwa Soil",
                    "irrigationType": "Tube-well with Drip System",
                    "location": "Gram Sanwer, Tehsil Sanwer, Indore"
                },
                "crops": [
                    {"cropId": "CRP-2009", "cropName": "Soyabean", "variety": "JS-335 Yellow", "sowing": 85, "harvest": 20, "area": 4.5, "yield": 45.0},
                    {"cropId": "CRP-2010", "cropName": "Chana (Chickpea)", "variety": "Desi Bold", "sowing": 95, "harvest": 15, "area": 2.7, "yield": 28.0}
                ],
                "bank": {
                    "bankAccountId": "BNK-5016",
                    "bankName": "Canara Bank",
                    "accountNumber": "12341010098765",
                    "ifscCode": "CNRB0001234",
                    "branch": "Sanwer Indore Branch",
                    "status": "Verified"
                },
                "procurement": {
                    "applicationId": "APP-44214",
                    "procurementId": "PRC-00128",
                    "centreId": "PRC-CTR-104",
                    "centreName": "Indore Malwa Krishi Mandi Centre",
                    "cropId": "CRP-2009",
                    "cropName": "Soyabean",
                    "variety": "JS-335 Yellow",
                    "qty": 35.0,
                    "slot": "11:00 AM - 01:00 PM",
                    "token": "TKN-022",
                    "queue": 2,
                    "wait": 25,
                    "status": "Produce Received",
                    "amount": 162750.0
                },
                "payment": None
            },
            {
                "farmerId": "FMR-88017",
                "fullName": "Pooja Sharma",
                "mobile": "9876543215",
                "email": "pooja.sharma@example.com",
                "password": "Password@123",
                "state": "Uttar Pradesh",
                "district": "Varanasi",
                "village": "Rohania",
                "land": {
                    "landId": "LND-1006",
                    "area": 3.8,
                    "unit": "Acres",
                    "soilType": "Alluvial Ganga Basin Soil",
                    "irrigationType": "Tube-well with Sprinkler",
                    "location": "Khasra 512, Rohania Village, Varanasi"
                },
                "crops": [
                    {"cropId": "CRP-2011", "cropName": "Mustard", "variety": "PM-30 High Oil", "sowing": 100, "harvest": 10, "area": 2.0, "yield": 22.0},
                    {"cropId": "CRP-2012", "cropName": "Wheat", "variety": "Sharbati Gold", "sowing": 90, "harvest": 25, "area": 1.8, "yield": 38.0}
                ],
                "bank": {
                    "bankAccountId": "BNK-5017",
                    "bankName": "Union Bank of India",
                    "accountNumber": "301102010098765",
                    "ifscCode": "UBIN0530115",
                    "branch": "Varanasi Cantt Branch",
                    "status": "Verified"
                },
                "procurement": {
                    "applicationId": "APP-44215",
                    "procurementId": "PRC-00129",
                    "centreId": "PRC-CTR-101",
                    "centreName": "Karnal APMC Grain Procurement Hub",
                    "cropId": "CRP-2011",
                    "cropName": "Mustard",
                    "variety": "PM-30 High Oil",
                    "qty": 20.0,
                    "slot": "02:00 PM - 04:00 PM",
                    "token": "TKN-014",
                    "queue": 1,
                    "wait": 10,
                    "status": "Payment Initiated",
                    "amount": 113000.0
                },
                "payment": {
                    "paymentId": "PAY-00893",
                    "amount": 113000.0,
                    "status": "Payment Processing",
                    "remarks": "PFMS DBT Electronic Clearing in progress for 20 Quintals Mustard"
                }
            }
        ]

        # Loop and upsert all 6 demo farmers
        for acc in demo_accounts:
            existing = db_manager.farmers.find_one({"mobile": acc["mobile"]})
            if not existing:
                fid = acc["farmerId"]
                f_doc = {
                    "farmerId": fid,
                    "fullName": acc["fullName"],
                    "mobile": acc["mobile"],
                    "email": acc["email"],
                    "hashedPassword": hash_password(acc["password"]),
                    "state": acc["state"],
                    "district": acc["district"],
                    "village": acc["village"],
                    "created_at": now,
                    "updated_at": now
                }
                db_manager.farmers.insert_one(f_doc)

                # Land
                l_info = acc["land"]
                db_manager.land_records.insert_one({
                    "landId": l_info["landId"],
                    "farmerId": fid,
                    "area": float(l_info["area"]),
                    "unit": l_info["unit"],
                    "soilType": l_info["soilType"],
                    "irrigationType": l_info["irrigationType"],
                    "location": l_info["location"],
                    "created_at": now
                })

                # Crops
                for cr in acc["crops"]:
                    db_manager.crops.insert_one({
                        "cropId": cr["cropId"],
                        "farmerId": fid,
                        "cropName": cr["cropName"],
                        "variety": cr["variety"],
                        "sowingDate": (now - timedelta(days=cr["sowing"])).strftime("%Y-%m-%d"),
                        "expectedHarvest": (now + timedelta(days=cr["harvest"])).strftime("%Y-%m-%d"),
                        "cultivatedArea": float(cr["area"]),
                        "areaUnit": "Acres",
                        "estimatedYieldQuintals": float(cr["yield"]),
                        "created_at": now
                    })

                # Bank
                b_info = acc["bank"]
                raw_a = b_info["accountNumber"]
                db_manager.bank_accounts.insert_one({
                    "bankAccountId": b_info["bankAccountId"],
                    "farmerId": fid,
                    "bankName": b_info["bankName"],
                    "accountHolder": acc["fullName"],
                    "accountNumber": raw_a,
                    "maskedAccountNumber": mask_account_number(raw_a),
                    "ifscCode": b_info["ifscCode"],
                    "branchName": b_info["branch"],
                    "verificationStatus": b_info["status"],
                    "verifiedAt": now.isoformat(),
                    "created_at": now
                })

                # Procurement
                p_info = acc["procurement"]
                if p_info:
                    db_manager.procurement_applications.insert_one({
                        "applicationId": p_info["applicationId"],
                        "procurementId": p_info["procurementId"],
                        "farmerId": fid,
                        "centreId": p_info["centreId"],
                        "centreName": p_info["centreName"],
                        "cropId": p_info["cropId"],
                        "cropName": p_info["cropName"],
                        "variety": p_info["variety"],
                        "quantityQuintals": float(p_info["qty"]),
                        "bookingDate": now.strftime("%Y-%m-%d"),
                        "timeSlot": p_info["slot"],
                        "tokenNumber": p_info["token"],
                        "queuePosition": p_info["queue"],
                        "estimatedWaitMinutes": p_info["wait"],
                        "status": p_info["status"],
                        "qualityGrade": "Grade A (FAQ Passed)",
                        "moisturePercent": 11.4,
                        "ratePerQuintal": round(p_info["amount"] / p_info["qty"], 2),
                        "totalAmount": float(p_info["amount"]),
                        "created_at": now
                    })

                # Payment
                pay_info = acc["payment"]
                if pay_info and p_info:
                    db_manager.payments.insert_one({
                        "paymentId": pay_info["paymentId"],
                        "procurementId": p_info["procurementId"],
                        "applicationId": p_info["applicationId"],
                        "farmerId": fid,
                        "crop": p_info["cropName"],
                        "quantityQuintals": float(p_info["qty"]),
                        "ratePerQuintal": round(pay_info["amount"] / p_info["qty"], 2),
                        "amount": float(pay_info["amount"]),
                        "bankAccountId": b_info["bankAccountId"],
                        "bankName": b_info["bankName"],
                        "maskedAccountNumber": mask_account_number(raw_a),
                        "status": pay_info["status"],
                        "initiatedAt": now.isoformat(),
                        "creditedAt": now.isoformat() if pay_info["status"] == "Payment Credited" else None,
                        "remarks": pay_info["remarks"],
                        "created_at": now
                    })

                logger.info(f"Seeded demo farmer {acc['fullName']} ({acc['mobile']}) successfully.")

    except Exception as e:
        logger.error(f"Error during data seeding: {e}")
