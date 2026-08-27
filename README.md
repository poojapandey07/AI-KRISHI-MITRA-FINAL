# 🌱 AI Krishi Mitra — Modular Farmer Agriculture Platform

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat&logo=python)](https://python.org)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248.svg?style=flat&logo=mongodb)](https://mongodb.com)
[![Frontend](https://img.shields.io/badge/Frontend-HTML5%20%7C%20CSS3%20%7C%20Vanilla%20JS-E34F26.svg?style=flat)](https://developer.mozilla.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**AI Krishi Mitra** is a production-grade, modular, farmer-facing agriculture web application. Designed for collaborative development across **6 independent developer modules**, it provides Indian farmers with a single unified, mobile-first portal for farm management, APMC mandi queue slot booking, direct DBT payout tracking, AI crop quality grading, computer-vision plant pathology, and live mandi market linkage.

---

## 🏗️ 6-Module Architecture & Team Division

The codebase is technically decoupled so six developers can work on their respective modules independently without merge conflicts:

| Module | Developer Role | Frontend Directory | Backend Directory | Key Responsibilities |
| :--- | :--- | :--- | :--- | :--- |
| **Module 1** | **👨‍🌾 Farmer & Auth** | `frontend/modules/farmer/` | `backend/modules/farmer/` | Registration, JWT auth, Farmer Profile, Land Parcels, Crop cultivation |
| **Module 2** | **🏪 Procurement** | `frontend/modules/procurement/` | `backend/modules/procurement/` | APMC Centre discovery, Slot booking, Real-time Queue tokens, Status timeline |
| **Module 3** | **🏦 Krishi Finance** | `frontend/modules/finance/` | `backend/modules/finance/` | Bank account linking, NPCI sandbox verification, DBT procurement payout tracking |
| **Module 4** | **🤖 AI Standards** | `frontend/modules/ai-standards/` | `backend/modules/ai-standards/` | FCI/Agmark crop quality grader, Moisture/Foreign matter checks, Agronomy advice |
| **Module 5** | **🌱 Disease & Pest AI** | `frontend/modules/disease-pest-ai/` | `backend/modules/disease-pest-ai/` | Multipart leaf image upload, Computer-vision pathology inference, Rx prescriptions |
| **Module 6** | **📈 Market Linkage** | `frontend/modules/market-linkage/` | `backend/modules/market-linkage/` | Live Mandi spot prices, Price trend tickers, Verified institutional buyer contracts |

---

## 📂 Project Structure

```text
AI-KRISHI-MITRA/
│
├── frontend/
│   ├── index.html                  # Unified farmer portal shell
│   ├── assets/
│   │   ├── images/
│   │   └── icons/logo.svg          # Agriculture SVG brand icon
│   ├── css/
│   │   ├── variables.css           # Natural green & fintech color tokens, radii, shadows
│   │   ├── global.css              # Typography, layout shell, buttons, forms, tables, modals
│   │   └── responsive.css          # Mobile-first breakpoints (≤768px off-canvas drawer)
│   ├── js/
│   │   ├── api.js                  # Centralized fetch wrapper with JWT Bearer injection & error handler
│   │   ├── auth.js                 # Session management, login/register, local storage sync
│   │   ├── utils.js                # Toasts, currency formatting (₹), date formatters, badges
│   │   └── app.js                  # Master SPA router & unified live dashboard aggregator
│   └── modules/
│       ├── farmer/                 # Module 1 (farmer.html, farmer.css, farmer.js)
│       ├── procurement/            # Module 2 (procurement.html, procurement.css, procurement.js)
│       ├── finance/                # Module 3 (finance.html, finance.css, finance.js)
│       ├── ai-standards/           # Module 4 (standards.html, standards.css, standards.js)
│       ├── disease-pest-ai/        # Module 5 (disease.html, disease.css, disease.js)
│       └── market-linkage/         # Module 6 (market.html, market.css, market.js)
│
├── backend/
│   ├── main.py                     # FastAPI application, CORS, static mounting, router mounting
│   ├── config/
│   │   ├── database.py             # PyMongo database connection manager with index creators
│   │   └── settings.py             # Pydantic BaseSettings loading .env configuration
│   ├── middleware/
│   │   └── auth.py                 # JWT dependency injection (get_current_farmer)
│   ├── shared/
│   │   ├── schemas/common.py       # Standard ApiResponse and ErrorResponse models
│   │   ├── utils/security.py       # Bcrypt hashing, PyJWT encoder, account masking (•••• 1234)
│   │   └── services/seed_data.py   # Pre-seeds APMC centres, mandi rates, buyers, and demo farmer
│   └── modules/
│       ├── farmer/                 # router.py, service.py, model.py, schema.py
│       ├── procurement/            # router.py, service.py, model.py, schema.py
│       ├── finance/                # router.py, service.py, model.py, schema.py
│       ├── ai-standards/           # router.py, service.py, model.py, schema.py
│       ├── disease-pest-ai/        # router.py, service.py, model.py, schema.py
│       └── market-linkage/         # router.py, service.py, model.py, schema.py
│
├── tests/
│   └── test_api_flow.py            # Automated 20-step end-to-end integration test suite
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
└── README.md                       # Comprehensive documentation
```

---

## 🔄 End-to-End Farmer Flow

```text
1. Farmer Registration & Login
   │
   ▼
2. My Farm Management
   ├── Add Land Parcel (Acres, Soil Type, Irrigation)
   └── Add Crop (Wheat HD-2967, Sowing, Harvest Date)
   │
   ▼
3. Procurement Booking (APMC Mandi)
   ├── Select Centre (e.g. Karnal APMC Hub)
   ├── Select Crop & Quantity (30 Quintals)
   ├── Pick Date & Time Slot
   └── Generates: Application ID (APP-XXXXX), Procurement ID (PRC-XXXXX), Token (TKN-XX)
   │
   ▼
4. Real-time Status Timeline
   Application Submitted ➔ Slot Confirmed ➔ Produce Received ➔ Quality Checked ➔ Procurement Accepted
   │
   ▼
5. Payment Initiated (Cross-Module Automatic Trigger)
   └── Automatically creates linked payment record in Krishi Finance module (₹72,750)
   │
   ▼
6. Krishi Finance Settlement
   ├── Link Bank Account (Securely masked as •••• •••• •••• 1234)
   ├── NPCI Penny-Drop Sandbox Verification ➔ Verified
   └── Advance Status ➔ Payment Processing ➔ Payment Credited (Direct DBT)
   │
   ▼
7. Parallel AI & Market Linkages
   ├── AI Standards Grader: Evaluates moisture & foreign matter against FCI Fair Average Quality specs
   ├── Crop Health AI: Multipart leaf camera upload diagnosing Yellow Rust, Early Blight, Rice Blast, etc.
   └── Market Linkage: Real-time Mandi spot prices & institutional contract buyer connection
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.14)
- **MongoDB** running locally on `mongodb://localhost:27017/` (or MongoDB Atlas URI)

### 2. Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-org/ai-krishi-mitra.git
cd ai-krishi-mitra

# Create virtual environment (optional but recommended)
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create local environment configuration
copy .env.example .env
```

### 3. Run the Platform

```bash
# Start FastAPI backend with automatic reloading:
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

When started, the backend:
1. Automatically connects to MongoDB and creates optimal indexes.
2. Pre-seeds realistic procurement centres, live mandi rates, corporate buyer leads, and a demo farmer account.
3. Serves the web frontend at `http://127.0.0.1:8000/portal/index.html` (or simply `http://127.0.0.1:8000/` in your browser).
4. Serves interactive Swagger API docs at `http://127.0.0.1:8000/docs`.

---

## 👨‍🌾 Pre-Seeded Demo Account

You can log in immediately using the pre-seeded demo farmer credentials:

- **Mobile:** `9876543210`
- **Password:** `Password@123`
- *(Or click the "⚡ Fill Demo Account" button on the login screen)*

---

## 🧪 Running Automated Tests

A 20-step integration test suite verifies the end-to-end user journey:

```bash
python tests/test_api_flow.py
```

**Test Coverage:**
- System health & MongoDB live ping
- Demo authentication & new farmer registration
- Adding land parcel & crop registration
- Centre discovery & slot booking
- Queue status lookup
- Bank account linking & security masking
- NPCI sandbox verification
- Advancing procurement status to `Payment Initiated`
- Auto-creation of linked payment record in Krishi Finance
- Simulating payment status progression to `Payment Credited`
- FCI / Agmark quality standards grading algorithm
- Personalized agronomy recommendations
- Multipart image plant pathology inference
- Live mandi price searches & buyer lead generation

---

## 🌿 Git Branching Strategy for 6 Developers

To ensure smooth multi-developer collaboration, follow this Git branch convention:

```text
main           # Production-ready releases
  └── develop  # Integration branch
        ├── feature/farmer          (Member 1: frontend/modules/farmer/, backend/modules/farmer/)
        ├── feature/procurement     (Member 2: frontend/modules/procurement/, backend/modules/procurement/)
        ├── feature/finance         (Member 3: frontend/modules/finance/, backend/modules/finance/)
        ├── feature/ai-standards    (Member 4: frontend/modules/ai-standards/, backend/modules/ai-standards/)
        ├── feature/disease-pest    (Member 5: frontend/modules/disease-pest-ai/, backend/modules/disease-pest-ai/)
        └── feature/market-linkage  (Member 6: frontend/modules/market-linkage/, backend/modules/market-linkage/)
```

### Team Rules:
1. **Never commit module-specific code outside your module directory.**
2. Shared utilities must be added to `frontend/js/`, `frontend/css/`, or `backend/shared/`.
3. All database operations must go through `service.py` to keep routes thin and maintainable.
4. Merge into `develop` only after running `python tests/test_api_flow.py`.

---

## 🔐 Security & Architecture Highlights

- **Password Security:** Salted bcrypt password hashing (`bcrypt`).
- **Stateless Authentication:** PyJWT token verification with configurable expiration.
- **Financial Data Protection:** Bank account numbers are encrypted/stored securely and always masked (e.g. `•••• •••• •••• 1234`) across all API responses.
- **Pluggable AI Inference:** The disease analysis module features an abstract base predictor `BaseMLInferenceEngine`, allowing hot-swapping the mock engine with PyTorch, TensorFlow, or ONNX models without touching the routing layer.
- **Strict Separation of Concerns:** Route handlers (`router.py`) $\rightarrow$ Business logic (`service.py`) $\rightarrow$ Database manager (`config/database.py`).

---

## 📄 License
This project is licensed under the MIT License.
#   A I - K R I S H I - M I T R A - F I N A L  
 