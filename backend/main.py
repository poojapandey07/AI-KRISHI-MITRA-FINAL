import sys
import os
import importlib
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from config.settings import settings
from config.database import db_manager
from shared.services.seed_data import seed_initial_data

# Import Module Routers
from modules.farmer.router import auth_router, farmer_router
from modules.procurement.router import router as procurement_router
from modules.finance.router import router as finance_router

# Hyphenated directory router imports via importlib
ai_standards_module = importlib.import_module("modules.ai-standards.router")
ai_standards_router = ai_standards_module.router

disease_module = importlib.import_module("modules.disease-pest-ai.router")
disease_router = disease_module.router

market_module = importlib.import_module("modules.market-linkage.router")
market_router = market_module.router

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ai_krishi_mitra")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect DB & Seed initial data
    logger.info("Initializing AI Krishi Mitra platform backend...")
    db_manager.connect()
    seed_initial_data()
    logger.info("AI Krishi Mitra startup completed successfully.")
    yield
    # Shutdown: Disconnect DB
    logger.info("Shutting down AI Krishi Mitra platform backend...")
    db_manager.close()

app = FastAPI(
    title="AI Krishi Mitra — Modular Farmer Agriculture Platform",
    description=(
        "Production-grade, modular agricultural backend API supporting 6 developer modules:\n"
        "1. Farmer & Authentication\n"
        "2. Procurement Management\n"
        "3. Krishi Finance\n"
        "4. AI Standards & Recommendations\n"
        "5. Disease & Pest AI\n"
        "6. Market Linkage & Integration"
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS Configuration
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in origins else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Router Registrations ----------------- #

# 1. Farmer & Authentication
app.include_router(auth_router, prefix="/api/auth", tags=["1. Authentication"])
app.include_router(farmer_router, prefix="/api/farmers", tags=["1. Farmer Profile, Land & Crops"])

# 2. Procurement Management
app.include_router(procurement_router, prefix="/api/procurement", tags=["2. Procurement Management"])

# 3. Krishi Finance
app.include_router(finance_router, prefix="/api/finance", tags=["3. Krishi Finance"])

# 4. AI Standards + Recommendation
app.include_router(ai_standards_router, prefix="/api/ai", tags=["4. AI Standards & Recommendations"])

# 5. Disease & Pest AI
app.include_router(disease_router, prefix="/api/disease-analysis", tags=["5. Disease & Pest AI"])

# 6. Market Linkage + Integration
app.include_router(market_router, prefix="/api/market", tags=["6. Market Linkage"])

from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

frontend_dir = os.path.abspath(os.path.join(backend_dir, "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/portal", StaticFiles(directory=frontend_dir, html=True), name="portal")

# ----------------- Root & Health Check ----------------- #

@app.get("/", tags=["System"])
def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept and os.path.exists(frontend_dir):
        return RedirectResponse(url="/portal/index.html")
    return {
        "platform": "AI Krishi Mitra",
        "tagline": "Empowering Indian Farmers with Modular AI & Agriculture Services",
        "version": settings.APP_VERSION,
        "portal": "/portal/index.html",
        "docs": "/docs",
        "status": "Online"
    }

@app.get("/api/health", tags=["System"])
def health_check():
    db_connected = False
    stats = {}
    try:
        if db_manager.client:
            db_manager.client.admin.command('ping')
            db_connected = True
            stats = {
                "farmers": db_manager.farmers.count_documents({}),
                "procurementCentres": db_manager.procurement_centres.count_documents({}),
                "procurementApplications": db_manager.procurement_applications.count_documents({}),
                "payments": db_manager.payments.count_documents({}),
                "marketPrices": db_manager.market_prices.count_documents({}),
                "buyers": db_manager.buyers.count_documents({})
            }
    except Exception as e:
        logger.warning(f"Health check DB error: {e}")

    return {
        "status": "healthy" if db_connected else "degraded",
        "database": "connected" if db_connected else "disconnected",
        "databaseName": settings.DATABASE_NAME,
        "collections": stats
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
