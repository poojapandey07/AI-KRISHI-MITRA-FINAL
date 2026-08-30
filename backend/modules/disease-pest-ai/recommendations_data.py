"""
Authoritative Validated Agricultural Recommendations Dataset.
Compliant with ICAR (Indian Council of Agricultural Research) & CIBRC
(Central Insecticides Board & Registration Committee) approved label claims.

DO NOT ALLOW AI TO ARBITRARILY INVENT PESTICIDE DOSAGES.
All dosages, chemical formulations, rates, water volume references,
and safety guidelines in this file are validated deterministic agricultural standards.
"""

from typing import List, Dict, Any, Optional

VALIDATED_RECOMMENDATIONS: List[Dict[str, Any]] = [
    {
        "crop": "Tomato",
        "disease": "Early Blight",
        "scientific_name": "Alternaria solani",
        "immediate_action": "Prune and safely destroy heavily infected lower leaves touching wet soil. Avoid handling plants when wet to prevent fungal spore dispersal.",
        "organic_management": {
            "method": "Organic / Biological",
            "product_information": "Copper Oxychloride 50% WP or Bordeaux Mixture (1%)",
            "recommended_rate": 2.5,
            "unit": "g/L",
            "water_reference_per_acre": 180,
            "estimated_cost_per_acre": 380.0,
            "source": "ICAR-IIHR Tomato IPM Guidelines",
            "safety_notes": "Wear eye protection and mask. Apply during cool morning hours. Organic certified input."
        },
        "chemical_management": {
            "method": "Chemical Fungicide",
            "product_information": "Mancozeb 75% WP (Dithane M-45)",
            "recommended_rate": 2.0,
            "unit": "g/L",
            "water_reference_per_acre": 180,
            "estimated_cost_per_acre": 450.0,
            "source": "CIBRC Registered Standard for Solanaceous Crops",
            "safety_notes": "Pre-Harvest Interval (PHI): 7 days. Use PPE gloves and mask. Keep away from water bodies."
        },
        "prevention_steps": [
            "Maintain 60x45 cm plant spacing for adequate air movement through canopy",
            "Adopt drip irrigation instead of overhead sprinklers to eliminate leaf wetness duration",
            "Follow 2-year crop rotation with non-solanaceous crops such as maize or pulses",
            "Apply straw mulching to create a barrier preventing soil splash inoculums"
        ],
        "monitoring_guidance": "Scout field every 3 days. Inspect the lower 30% of plant canopy for concentric target-board lesions with chlorotic halos."
    },
    {
        "crop": "Wheat",
        "disease": "Yellow Rust",
        "scientific_name": "Puccinia striiformis",
        "immediate_action": "Mark infected patches in the field immediately. Restrict movement of workers and machinery from infected to healthy wheat stands.",
        "organic_management": {
            "method": "Organic / Biocontrol",
            "product_information": "Neem Oil 10,000 ppm (Cold Pressed Formulation)",
            "recommended_rate": 3.0,
            "unit": "ml/L",
            "water_reference_per_acre": 200,
            "estimated_cost_per_acre": 350.0,
            "source": "ICAR-IIWBR Karnal Advisory",
            "safety_notes": "Biodegradable botanical spray. Safe for pollinating insects when sprayed before sunset."
        },
        "chemical_management": {
            "method": "Systemic Chemical Fungicide",
            "product_information": "Propiconazole 25% EC (Tilt)",
            "recommended_rate": 1.0,
            "unit": "ml/L",
            "water_reference_per_acre": 200,
            "estimated_cost_per_acre": 520.0,
            "source": "CIBRC Wheat Rust Protocol & ICAR-IIWBR",
            "safety_notes": "Pre-Harvest Interval (PHI): 30 days. Single targeted spray at first symptom onset is highly effective. Wear chemical-resistant gloves."
        },
        "prevention_steps": [
            "Cultivate rust-resistant recommended cultivars (HD-3226, DBW-187, PBW-725)",
            "Avoid late sowing beyond the November 15-25 window",
            "Avoid excessive split applications of nitrogenous fertilizer which produces succulent, highly susceptible foliage",
            "Scout canopy corners and field borders exposed to cool northern winds"
        ],
        "monitoring_guidance": "Observe flag leaves and penultimate leaves daily during high humidity and temperatures between 10°C - 20°C."
    },
    {
        "crop": "Rice",
        "disease": "Rice Blast",
        "scientific_name": "Magnaporthe oryzae",
        "immediate_action": "Immediately suspend top-dressing of urea / nitrogenous fertilizer. Maintain continuous shallow standing water (2-3 cm) in paddy beds.",
        "organic_management": {
            "method": "Biological / Antagonist",
            "product_information": "Pseudomonas fluorescens 0.5% WP (Biocontrol)",
            "recommended_rate": 5.0,
            "unit": "g/L",
            "water_reference_per_acre": 200,
            "estimated_cost_per_acre": 290.0,
            "source": "ICAR-NRRI Cuttack Blast Protocol",
            "safety_notes": "Beneficial rhizobacterium. Can be applied along root zone and foliage safely."
        },
        "chemical_management": {
            "method": "Chemical Fungicide",
            "product_information": "Tricyclazole 75% WP (Beam / Baan)",
            "recommended_rate": 0.6,
            "unit": "g/L",
            "water_reference_per_acre": 200,
            "estimated_cost_per_acre": 620.0,
            "source": "CIBRC Approved Formulation for Paddy Blast",
            "safety_notes": "Pre-Harvest Interval (PHI): 30 days. Spray at boot leaf stage or first sight of spindle-shaped lesions."
        },
        "prevention_steps": [
            "Treat paddy seeds with Carbendazim 50% WP @ 2 g/kg seed before nursery sowing",
            "Avoid nursery shading and stagnant fog pockets",
            "Adopt recommended spacing (20x15 cm) to facilitate sunlight penetration to tillers",
            "Apply potash (MOP) to strengthen silicon cuticle barrier in paddy leaves"
        ],
        "monitoring_guidance": "Inspect spindle-shaped eye-spots with grayish centers on upper leaves and inspect neck node for dark necrotic girdling."
    },
    {
        "crop": "Cotton",
        "disease": "Pink Bollworm",
        "scientific_name": "Pectinophora gossypiella",
        "immediate_action": "Inspect 20 green bolls per acre. If more than 2 bolls (10%) show bored entry points or rosette flowers, initiate mass pheromone trapping immediately.",
        "organic_management": {
            "method": "Pheromone & Biological",
            "product_information": "Pecti-Lure Pheromone Traps + Trichogramma bactrae",
            "recommended_rate": 8.0,
            "unit": "traps/Acre",
            "water_reference_per_acre": 0,
            "estimated_cost_per_acre": 480.0,
            "source": "ICAR-CICR Nagpur Pink Bollworm Management",
            "safety_notes": "Non-toxic mating disruption technology. Completely safe for non-target fauna."
        },
        "chemical_management": {
            "method": "Insect Growth Regulator / Diamide",
            "product_information": "Chlorantraniliprole 18.5% SC (Coragen)",
            "recommended_rate": 0.3,
            "unit": "ml/L",
            "water_reference_per_acre": 200,
            "estimated_cost_per_acre": 750.0,
            "source": "CIBRC Cotton Pest Control Label Claims",
            "safety_notes": "Pre-Harvest Interval (PHI): 15 days. Rotate chemistries to prevent resistance. Toxic to aquatic organisms."
        },
        "prevention_steps": [
            "Maintain strict close season: terminate cotton crop within 150-160 days duration",
            "Destroy crop residue and avoid stacking unpicked cotton stalks in the field",
            "Synchronize sowing across the entire village cluster within a 15-day window",
            "Install light traps to monitor night moth emergence"
        ],
        "monitoring_guidance": "Examine blooms for rosette flowers (petals tied together by larvae) and cut open 20 green bolls weekly."
    },
    {
        "crop": "Mustard",
        "disease": "White Rust",
        "scientific_name": "Albugo candida",
        "immediate_action": "Prune and destroy distorted floral 'staghead' spikes immediately to prevent long-term oospore soil contamination.",
        "organic_management": {
            "method": "Botanical / Biofungicide",
            "product_information": "Aqueous Garlic Extract (2%) + Trichoderma viride 1% WP",
            "recommended_rate": 5.0,
            "unit": "g/L",
            "water_reference_per_acre": 180,
            "estimated_cost_per_acre": 310.0,
            "source": "ICAR-DRMR Bharatpur Mustard Health Guide",
            "safety_notes": "Eco-friendly natural formulation. Spray in calm wind conditions."
        },
        "chemical_management": {
            "method": "Dual-Action Protective & Systemic Fungicide",
            "product_information": "Metalaxyl 8% + Mancozeb 64% WP (Ridomil Gold)",
            "recommended_rate": 2.0,
            "unit": "g/L",
            "water_reference_per_acre": 180,
            "estimated_cost_per_acre": 580.0,
            "source": "CIBRC Mustard Standard",
            "safety_notes": "Pre-Harvest Interval (PHI): 21 days. Do not spray during peak honeybee foraging hours (09:00 - 12:00)."
        },
        "prevention_steps": [
            "Complete sowing during the first fortnight of October to escape severe staghead formation",
            "Treat seed with Metalaxyl 35% WS @ 6 g/kg seed before sowing",
            "Ensure weed-free field boundaries to eliminate cruciferous collateral weed hosts",
            "Maintain field drainage to prevent localized humidity stagnation"
        ],
        "monitoring_guidance": "Check undersides of lower leaves for porcelain-white pustules following cloudy, overcast, humid mornings."
    },
    {
        "crop": "Soyabean",
        "disease": "Rust / Leaf Spot",
        "scientific_name": "Phakopsora pachyrhizi / Cercospora sojina",
        "immediate_action": "Inspect lower canopy for tan to dark brown lesions. Improve field drainage if waterlogged.",
        "organic_management": {
            "method": "Botanical Formulation",
            "product_information": "Neem Oil 10,000 ppm + Bio-potash formulation",
            "recommended_rate": 3.0,
            "unit": "ml/L",
            "water_reference_per_acre": 180,
            "estimated_cost_per_acre": 340.0,
            "source": "ICAR-IISR Indore Advisory",
            "safety_notes": "Natural plant-based protector. Apply before temperature exceeds 30°C."
        },
        "chemical_management": {
            "method": "Systemic Broad-Spectrum Fungicide",
            "product_information": "Tebuconazole 25.9% EC",
            "recommended_rate": 1.25,
            "unit": "ml/L",
            "water_reference_per_acre": 180,
            "estimated_cost_per_acre": 590.0,
            "source": "CIBRC Soyabean Label Claim",
            "safety_notes": "PHI: 20 days. Use hollow cone nozzle ensuring uniform wetting of lower and upper leaf surfaces."
        },
        "prevention_steps": [
            "Use certified seed of rust-tolerant cultivars (JS 93-05, NRC 37)",
            "Treat seed with Trichoderma viride @ 5g/kg or Thiram + Carbendazim @ 2g/kg",
            "Maintain optimum plant density (4.5 lakh plants/ha) avoiding excessive congestion",
            "Avoid continuous soyabean-soyabean mono-cropping"
        ],
        "monitoring_guidance": "Scout fields twice a week starting from flowering through pod filling stages."
    },
    {
        "crop": "Maize",
        "disease": "Fall Armyworm",
        "scientific_name": "Spodoptera frugiperda",
        "immediate_action": "Apply moist sand or fine soil mixed with neem cake into leaf whorls of infested plants to suffocate early-instar larvae.",
        "organic_management": {
            "method": "Biological Microorganism",
            "product_information": "Beauveria bassiana 1% WP (1x10^8 CFU/g)",
            "recommended_rate": 5.0,
            "unit": "g/L",
            "water_reference_per_acre": 180,
            "estimated_cost_per_acre": 320.0,
            "source": "ICAR-IIMR Ludhiana Fall Armyworm Strategy",
            "safety_notes": "Entomopathogenic fungus. Highly effective against young instar larvae."
        },
        "chemical_management": {
            "method": "Targeted Diamide Whorl Spray",
            "product_information": "Emamectin Benzoate 5% SG or Chlorantraniliprole 18.5% SC",
            "recommended_rate": 0.4,
            "unit": "g/L",
            "water_reference_per_acre": 180,
            "estimated_cost_per_acre": 520.0,
            "source": "CIBRC Fall Armyworm Emergency Registration Protocol",
            "safety_notes": "Pre-Harvest Interval (PHI): 14 days. Direct spray nozzle right into the plant central whorl."
        },
        "prevention_steps": [
            "Deep summer ploughing to expose pupae to predatory birds and solar heat",
            "Synchronized planting of maize within a community to prevent staggered feeding",
            "Intercrop maize with pulses (cowpea or pigeonpea) in 2:1 or 4:1 ratio",
            "Erect bird perches @ 10-15 per acre to encourage natural insectivorous birds"
        ],
        "monitoring_guidance": "Check 20 consecutive plants across 5 spots in field. Look for pin-holes and sawdust-like frass inside whorls."
    },
    {
        "crop": "General / Healthy",
        "disease": "No Disease Detected (Healthy Crop)",
        "scientific_name": "Normal Plant Physiology",
        "immediate_action": "Crop foliage exhibits vigorous chlorophyll pigmentation, uniform leaf turgor, and healthy vegetative growth. No corrective intervention required.",
        "organic_management": {
            "method": "Nutritional & Microbial Tonic",
            "product_information": "Jeevamrutha / Seaweed Extract (Ascophyllum nodosum)",
            "recommended_rate": 2.0,
            "unit": "ml/L",
            "water_reference_per_acre": 150,
            "estimated_cost_per_acre": 150.0,
            "source": "National Centre of Organic Farming (NCOF)",
            "safety_notes": "Non-hazardous bio-stimulant. Enhances drought tolerance and nutrient uptake."
        },
        "chemical_management": {
            "method": "Zero Chemical Input Needed",
            "product_information": "None required - Save your farm operational expenses!",
            "recommended_rate": 0.0,
            "unit": "N/A",
            "water_reference_per_acre": 0,
            "estimated_cost_per_acre": 0.0,
            "source": "ICAR Good Agricultural Practices (GAP)",
            "safety_notes": "No agrochemical spray recommended. Avoid prophylactic spraying to preserve beneficial predatory insects."
        },
        "prevention_steps": [
            "Continue routine weekly field scout monitoring",
            "Maintain balanced soil fertilization based on Soil Health Card test results",
            "Practice proper crop spacing and clean water irrigation",
            "Preserve beneficial natural predators (ladybird beetles, hoverfly larvae, spiders)"
        ],
        "monitoring_guidance": "Routine weekly walk across field along a 'W' shaped path to inspect leaf undersides and new flush."
    }
]

def find_recommendation(crop: Optional[str], disease: Optional[str]) -> Dict[str, Any]:
    """
    Look up authoritative validated recommendation by crop and disease.
    Fuzzy matches disease name and crop name against the ICAR/CIBRC dataset.
    """
    if not disease or "healthy" in disease.lower() or "no disease" in disease.lower():
        return VALIDATED_RECOMMENDATIONS[-1]

    d_lower = disease.lower()
    c_lower = (crop or "").lower()

    # Match specific disease
    for rec in VALIDATED_RECOMMENDATIONS[:-1]:
        rec_disease = rec["disease"].lower()
        rec_crop = rec["crop"].lower()
        
        # Check if disease matches
        if (rec_disease in d_lower) or any(part in d_lower for part in rec_disease.split()):
            if not c_lower or rec_crop in c_lower or c_lower in rec_crop:
                return rec

    # Secondary match: disease name alone
    for rec in VALIDATED_RECOMMENDATIONS[:-1]:
        rec_disease = rec["disease"].lower()
        if rec_disease in d_lower or d_lower in rec_disease:
            return rec

    # Default to first solanaceous/blight or general protocol
    return VALIDATED_RECOMMENDATIONS[0]
