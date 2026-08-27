import random
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from config.database import db_manager
from shared.utils.security import generate_id
from .schema import DiseaseAnalysisResponse, TreatmentAction

class BaseMLInferenceEngine(ABC):
    """
    Abstract interface for ML Disease Prediction Engines.
    Can be seamlessly implemented by:
    - TensorFlow / Keras (ResNet50, MobileNetV3)
    - PyTorch (VisionTransformer, EfficientNet)
    - ONNX Runtime
    - Mock / Heuristic Inference Engine
    """
    @abstractmethod
    def predict(self, image_bytes: bytes, filename: str) -> Dict[str, Any]:
        pass

class MockMLInferenceEngine(BaseMLInferenceEngine):
    """
    Realistic Agricultural Diagnostics Inference Engine.
    Uses image byte hashes and agricultural diagnostics patterns
    to produce rich, deterministic, farmer-usable diagnostic reports.
    """
    DIAGNOSIS_CATALOG = [
        {
            "crop": "Wheat",
            "disease": "Wheat Yellow Rust (Puccinia striiformis)",
            "severity": "High",
            "confidence_range": (91.0, 96.5),
            "symptoms": [
                "Bright yellowish linear stripes/pustules arranged parallel along leaf veins",
                "Powdery orange-yellow spores on finger contact",
                "Premature chlorosis and leaf desiccation reducing photosynthetic area"
            ],
            "organicTreatment": [
                "Spray 5% aqueous Neem Seed Kernel Extract (NSKE) or Neem oil at 3-5 ml/L",
                "Apply biocontrol formulation Trichoderma harzianum @ 5g/liter along base",
                "Dust sulfur powder at 20-25 kg/ha during cool morning hours"
            ],
            "chemicalRemedy": [
                "Spray Propiconazole 25% EC (Tilt) @ 1 ml per liter of water (500 ml/ha)",
                "Alternative: Tebuconazole 25.9% m/m EC @ 1-1.25 ml/liter",
                "Ensure spray coverage reaches lower canopy leaves with hollow cone nozzle"
            ],
            "preventiveMeasures": [
                "Sow rust-resistant varieties such as HD-3226, PBW-725, or DBW-187",
                "Avoid excessive nitrogenous fertilizer application which promotes lush susceptible growth",
                "Maintain optimal plant spacing to allow canopy air circulation"
            ],
            "urgencyText": "Action required within 48 hours to prevent spread to adjacent field parcels."
        },
        {
            "crop": "Tomato",
            "disease": "Early Blight (Alternaria solani)",
            "severity": "Moderate",
            "confidence_range": (88.5, 94.0),
            "symptoms": [
                "Concentric dark brown rings forming 'target-board' spots on older lower leaves",
                "Surrounding chlorotic yellow halos around necrotic lesions",
                "Stem cankers near soil line and sunken dark lesions on fruit stem ends"
            ],
            "organicTreatment": [
                "Spray Copper Oxychloride (50% WP) @ 2.5 g/L or Bordeaux mixture (1%)",
                "Foliar application of Pseudomonas fluorescens @ 10 g/L",
                "Mulch beds with clean straw to prevent soil-splash onto lower leaves"
            ],
            "chemicalRemedy": [
                "Spray Mancozeb 75% WP @ 2 g/L or Chlorothalonil 75% WP @ 2 g/L",
                "For severe spread: Azoxystrobin 23% SC @ 1 ml/L or Difenoconazole 25% EC @ 0.5 ml/L"
            ],
            "preventiveMeasures": [
                "Prune lower leaves touching wet soil to eliminate splash transmission",
                "Water via drip irrigation; avoid overhead sprinkler watering",
                "Rotate with non-solanaceous crops (pulses/maize) for 2 seasons"
            ],
            "urgencyText": "Apply protective fungicide before anticipated morning rain or high humidity."
        },
        {
            "crop": "Rice / Paddy",
            "disease": "Rice Blast (Magnaporthe oryzae)",
            "severity": "Critical",
            "confidence_range": (92.0, 97.8),
            "symptoms": [
                "Spindle or diamond-shaped lesions with grayish centers and dark reddish-brown borders",
                "Collar rot and neck blast resulting in drooping, chalky panicles (whiteheads)"
            ],
            "organicTreatment": [
                "Spray fermented buttermilk and garlic extract mixture (5%)",
                "Application of Pseudomonas fluorescens talc formulation @ 5 g/L"
            ],
            "chemicalRemedy": [
                "Spray Tricyclazole 75% WP @ 0.6 g/L (Beam / Baan) at early tillering and panicle emergence",
                "Alternative: Isoprothiolane 40% EC @ 1.5 ml/L"
            ],
            "preventiveMeasures": [
                "Avoid split application of urea during foggy, overcast weather",
                "Keep field inundated with recommended shallow water level",
                "Treat seed with Carboxin + Thiram before nursery broadcasting"
            ],
            "urgencyText": "Critical risk of lodging and panicle sterility. Spray immediately."
        },
        {
            "crop": "Cotton",
            "disease": "Pink Bollworm (Pectinophora gossypiella)",
            "severity": "High",
            "confidence_range": (89.0, 95.0),
            "symptoms": [
                "Rosetted blossoms that fail to open into normal flowers",
                "Bored holes in young green bolls sealed with frass",
                "Premature boll opening and stained, unspinnable lint"
            ],
            "organicTreatment": [
                "Install Pheromone Traps (Pecti-lure) @ 8-10 traps/acre for mass trapping",
                "Release egg parasitoid Trichogramma bactrae @ 60,000/acre weekly",
                "Spray Neem oil (10,000 ppm) @ 2 ml/L"
            ],
            "chemicalRemedy": [
                "Spray Chlorantraniliprole 18.5% SC @ 0.3 ml/L or Emamectin Benzoate 5% SG @ 0.5 g/L",
                "Alternate with Spinetoram 11.7% SC @ 1 ml/L if resistance is observed"
            ],
            "preventiveMeasures": [
                "Destroy stubbles and leftover bolls after final picking",
                "Avoid extending crop beyond 150-160 days duration",
                "Adopt synchronous sowing in farmer cluster"
            ],
            "urgencyText": "Inspect 20 bolls across field; spray if rosette flowers exceed 5% threshold."
        },
        {
            "crop": "Mustard",
            "disease": "White Rust (Albugo candida)",
            "severity": "Moderate",
            "confidence_range": (87.0, 93.5),
            "symptoms": [
                "White to creamy-yellow raised pustules (blisters) on leaf undersides",
                "Floral malformation called 'staghead' causing sterile swollen inflorescences"
            ],
            "organicTreatment": [
                "Foliar spray of 2% aqueous garlic extract",
                "Application of bio-fungicide Trichoderma viride @ 5 g/L"
            ],
            "chemicalRemedy": [
                "Spray Metalaxyl 8% + Mancozeb 64% WP (Ridomil MZ) @ 2 g/L",
                "Repeat after 12-14 days if fog and cloudy weather persist"
            ],
            "preventiveMeasures": [
                "Early sowing (first fortnight of October) escapes severe staghead phase",
                "Collect and burn infected floral stagheads to avoid oospore soil buildup"
            ],
            "urgencyText": "Spray at flowering onset before stagheads form on primary racemes."
        },
        {
            "crop": "Healthy Foliage",
            "disease": "No Disease Detected (Healthy Crop)",
            "severity": "Healthy",
            "confidence_range": (96.0, 99.2),
            "symptoms": [
                "Vibrant deep green chlorophyll coloration throughout leaf blade",
                "Intact leaf margins and vein structure with no visible necrotic spots or mildew",
                "Healthy turgor and active vegetative/reproductive development"
            ],
            "organicTreatment": [
                "Maintain regular Jeevamrutha or vermicompost tea drenching every 15 days",
                "Foliar spray of Seaweed extract (Ascophyllum nodosum) @ 2 ml/L for vigor"
            ],
            "chemicalRemedy": [
                "No chemical pesticides required at this time. Save input costs!"
            ],
            "preventiveMeasures": [
                "Continue routine weekly field scout monitoring",
                "Maintain balanced N-P-K fertilization according to soil health card specs"
            ],
            "urgencyText": "Crop is in peak physiological health. No corrective action needed."
        }
    ]

    def predict(self, image_bytes: bytes, filename: str) -> Dict[str, Any]:
        # Hash image bytes for reproducible, stable prediction per image
        hasher = hashlib.md5(image_bytes)
        hex_digest = hasher.hexdigest()
        seed_val = int(hex_digest[:8], 16)

        # Check if filename has hints
        fname_lower = filename.lower()
        matched_catalog = None
        if "rust" in fname_lower or "wheat" in fname_lower:
            matched_catalog = self.DIAGNOSIS_CATALOG[0]
        elif "tomato" in fname_lower or "blight" in fname_lower:
            matched_catalog = self.DIAGNOSIS_CATALOG[1]
        elif "rice" in fname_lower or "paddy" in fname_lower or "blast" in fname_lower:
            matched_catalog = self.DIAGNOSIS_CATALOG[2]
        elif "cotton" in fname_lower or "pest" in fname_lower or "bollworm" in fname_lower:
            matched_catalog = self.DIAGNOSIS_CATALOG[3]
        elif "mustard" in fname_lower:
            matched_catalog = self.DIAGNOSIS_CATALOG[4]
        elif "healthy" in fname_lower or "green" in fname_lower:
            matched_catalog = self.DIAGNOSIS_CATALOG[5]
        else:
            # Deterministic selection based on image content hash
            idx = seed_val % len(self.DIAGNOSIS_CATALOG)
            matched_catalog = self.DIAGNOSIS_CATALOG[idx]

        # Calculate confidence within range
        low, high = matched_catalog["confidence_range"]
        conf_ratio = (seed_val % 1000) / 1000.0
        confidence = round(low + conf_ratio * (high - low), 1)

        return {
            "cropDetected": matched_catalog["crop"],
            "possibleDisease": matched_catalog["disease"],
            "confidence": confidence,
            "severity": matched_catalog["severity"],
            "symptoms": matched_catalog["symptoms"],
            "recommendedAction": {
                "organicTreatment": matched_catalog["organicTreatment"],
                "chemicalRemedy": matched_catalog["chemicalRemedy"],
                "preventiveMeasures": matched_catalog["preventiveMeasures"],
                "urgencyText": matched_catalog["urgencyText"]
            }
        }

class DiseaseAIService:
    def __init__(self, engine: Optional[BaseMLInferenceEngine] = None):
        self.engine = engine or MockMLInferenceEngine()

    def set_engine(self, engine: BaseMLInferenceEngine):
        """Allows hot-swapping mock engine with TensorFlow / PyTorch / ONNX model."""
        self.engine = engine

    def analyze_crop_image(self, image_bytes: bytes, filename: str, farmer_id: Optional[str] = None) -> DiseaseAnalysisResponse:
        prediction = self.engine.predict(image_bytes, filename)
        analysis_id = generate_id("DIS", 5)
        now = datetime.now(timezone.utc)

        record = {
            "analysisId": analysis_id,
            "farmerId": farmer_id,
            "filename": filename,
            "cropDetected": prediction["cropDetected"],
            "possibleDisease": prediction["possibleDisease"],
            "confidence": prediction["confidence"],
            "severity": prediction["severity"],
            "symptoms": prediction["symptoms"],
            "recommendedAction": prediction["recommendedAction"],
            "created_at": now
        }

        # Store in MongoDB
        try:
            db_manager.disease_analyses.insert_one(record)
        except Exception:
            pass

        return DiseaseAnalysisResponse(
            analysisId=analysis_id,
            cropDetected=prediction["cropDetected"],
            possibleDisease=prediction["possibleDisease"],
            confidence=prediction["confidence"],
            severity=prediction["severity"],
            symptoms=prediction["symptoms"],
            recommendedAction=TreatmentAction(**prediction["recommendedAction"]),
            created_at=now.isoformat()
        )

    def get_analysis_history(self, farmer_id: str) -> List[DiseaseAnalysisResponse]:
        records = list(db_manager.disease_analyses.find({"farmerId": farmer_id}).sort("created_at", -1).limit(10))
        results = []
        for r in records:
            r["_id"] = str(r["_id"])
            if isinstance(r.get("created_at"), datetime):
                r["created_at"] = r["created_at"].isoformat()
            results.append(DiseaseAnalysisResponse(
                analysisId=r["analysisId"],
                cropDetected=r["cropDetected"],
                possibleDisease=r["possibleDisease"],
                confidence=r["confidence"],
                severity=r["severity"],
                symptoms=r.get("symptoms", []),
                recommendedAction=TreatmentAction(**r["recommendedAction"]),
                created_at=r["created_at"]
            ))
        return results

disease_ai_service = DiseaseAIService()
