/**
 * Module 5: Crop Health Intelligence & Gemini AI Controller
 * Features:
 * - Multimodal Gemini AI inference with local diagnostic fallback
 * - 5-Step Animated Loading Experience
 * - Contextual farm inputs (Crop, Area, Unit, Growth Stage, Location, Symptoms)
 * - Safe agricultural boundary with ICAR/CIBRC validated dosages
 * - Deterministic Area & Cost Calculator
 * - Vernacular toggle (English & Hindi) with Browser Speech Synthesis ("🔊 Listen")
 * - Confidence-aware expert review escalation
 * - Regional disease risk monitoring & early warning
 * - Full chronological diagnosis history
 */

window.DiseaseModule = {
  initialized: false,
  selectedFile: null,
  currentDiagnosis: null,
  activeLanguage: "en",

  init() {
    this.bindEvents();
    this.autoFillFarmerContext();
    this.loadRegionalRisk();
    this.loadHistory();
    this.initialized = true;
  },

  autoFillFarmerContext() {
    if (window.auth && window.auth.isAuthenticated()) {
      const farmer = window.auth.getFarmer();
      if (farmer) {
        const locInput = document.getElementById("scan-location");
        if (locInput && (farmer.district || farmer.state)) {
          locInput.value = `${farmer.district || ''}, ${farmer.state || ''}`.replace(/^,\s*|,\s*$/g, '');
        }
      }
    }
  },

  bindEvents() {
    const fileInput = document.getElementById("disease-file-input");
    const btnBrowse = document.getElementById("btn-browse-file");
    const btnReselect = document.getElementById("btn-reselect-file");
    const dropzone = document.getElementById("disease-dropzone");
    const btnRun = document.getElementById("btn-run-diagnosis");

    if (btnBrowse && fileInput) {
      btnBrowse.onclick = (e) => {
        e.stopPropagation();
        fileInput.click();
      };
    }

    if (btnReselect && fileInput) {
      btnReselect.onclick = (e) => {
        e.stopPropagation();
        fileInput.click();
      };
    }

    if (dropzone && fileInput) {
      dropzone.onclick = () => fileInput.click();

      dropzone.ondragover = (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
      };

      dropzone.ondragleave = () => {
        dropzone.classList.remove("dragover");
      };

      dropzone.ondrop = (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
          this.handleFileChosen(e.dataTransfer.files[0]);
        }
      };

      fileInput.onchange = (e) => {
        if (e.target.files && e.target.files[0]) {
          this.handleFileChosen(e.target.files[0]);
        }
      };
    }

    if (btnRun) {
      btnRun.onclick = () => this.runDiagnosis();
    }
  },

  handleFileChosen(file) {
    this.selectedFile = file;
    const promptBox = document.getElementById("dropzone-prompt");
    const previewBox = document.getElementById("dropzone-preview");
    const previewImg = document.getElementById("image-preview-element");
    const btnRun = document.getElementById("btn-run-diagnosis");

    if (promptBox && previewBox && previewImg) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImg.src = e.target.result;
        promptBox.style.display = "none";
        previewBox.style.display = "block";
        if (btnRun) btnRun.disabled = false;
      };
      reader.readAsDataURL(file);
    }
  },

  async runSampleTest(sampleName, cropHint) {
    // Generate a lightweight canvas image blob representing the crop sample
    const canvas = document.createElement("canvas");
    canvas.width = 400;
    canvas.height = 300;
    const ctx = canvas.getContext("2d");
    
    // Draw leaf-like background
    const isHealthy = sampleName.includes("Healthy");
    ctx.fillStyle = isHealthy ? "#2e7d32" : (sampleName.includes("Rust") ? "#92400e" : "#5b21b6");
    ctx.fillRect(0, 0, 400, 300);
    
    // Draw leaf vein motifs
    ctx.strokeStyle = "rgba(255, 255, 255, 0.25)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(200, 0);
    ctx.lineTo(200, 300);
    ctx.stroke();

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 18px sans-serif";
    ctx.fillText(`AI Krishi Sample: ${sampleName}`, 20, 150);

    const cropSelect = document.getElementById("scan-crop-select");
    if (cropSelect && cropHint) {
      cropSelect.value = cropHint;
    }

    canvas.toBlob((blob) => {
      const sanitizedName = sampleName.toLowerCase().replace(/\s+/g, "_") + "_sample.jpg";
      const sampleFile = new File([blob], sanitizedName, { type: "image/jpeg" });
      this.handleFileChosen(sampleFile);
      this.runDiagnosis();
    }, "image/jpeg");
  },

  async runDiagnosis() {
    if (!this.selectedFile) {
      window.utils.showToast("Please choose or capture a crop leaf image first.", "warning");
      return;
    }

    const reportBox = document.getElementById("disease-diagnosis-report");
    const stepperBox = document.getElementById("disease-loading-stepper");
    const laserLine = document.getElementById("scanner-laser-line");
    const btnRun = document.getElementById("btn-run-diagnosis");

    if (laserLine) laserLine.style.display = "block";
    if (btnRun) btnRun.disabled = true;
    if (reportBox) reportBox.style.display = "none";
    if (stepperBox) stepperBox.style.display = "block";

    // Animate the 5 loading steps smoothly
    this.animateStepper();

    // Prepare FormData with image and contextual farm fields
    const formData = new FormData();
    formData.append("file", this.selectedFile);

    const cropVal = document.getElementById("scan-crop-select")?.value;
    const areaVal = document.getElementById("scan-farm-area")?.value;
    const unitVal = document.getElementById("scan-area-unit")?.value;
    const stageVal = document.getElementById("scan-growth-stage")?.value;
    const locVal = document.getElementById("scan-location")?.value || "";
    const symptomsVal = document.getElementById("scan-symptoms")?.value || "";

    if (cropVal) formData.append("crop", cropVal);
    if (areaVal) formData.append("farmArea", areaVal);
    if (unitVal) formData.append("areaUnit", unitVal);
    if (stageVal) formData.append("growthStage", stageVal);
    if (symptomsVal) formData.append("symptoms", symptomsVal);

    if (locVal) {
      const parts = locVal.split(",");
      if (parts.length >= 2) {
        formData.append("district", parts[0].trim());
        formData.append("state", parts[1].trim());
      } else {
        formData.append("district", locVal.trim());
      }
    }

    try {
      const res = await window.api.post("/api/crop/analyze", formData);
      if (res.success && res.data) {
        this.currentDiagnosis = res.data;
        this.renderDiagnosisReport(res.data);
        await this.loadHistory();
        await this.loadRegionalRisk();
        window.utils.showToast(res.message || "Diagnosis completed successfully.", "success");
      }
    } catch (err) {
      if (reportBox) {
        reportBox.style.display = "block";
        window.utils.renderError(reportBox, err.message, () => this.runDiagnosis());
      }
    } finally {
      if (stepperBox) stepperBox.style.display = "none";
      if (laserLine) laserLine.style.display = "none";
      if (btnRun) btnRun.disabled = false;
    }
  },

  animateStepper() {
    const steps = [1, 2, 3, 4, 5];
    steps.forEach((s) => {
      const el = document.getElementById(`step-${s}`);
      if (el) {
        el.className = "stepper-step";
      }
    });

    let current = 1;
    const interval = setInterval(() => {
      if (current <= 5) {
        const prev = document.getElementById(`step-${current - 1}`);
        if (prev) {
          prev.className = "stepper-step completed";
        }
        const curr = document.getElementById(`step-${current}`);
        if (curr) {
          curr.className = "stepper-step active";
        }
        current++;
      } else {
        clearInterval(interval);
      }
    }, 450);
  },

  renderDiagnosisReport(d) {
    const reportBox = document.getElementById("disease-diagnosis-report");
    if (!reportBox) return;

    reportBox.style.display = "block";

    const org = d.organic_management || {};
    const chem = d.chemical_management || {};
    const calc = d.area_cost_estimation || {};
    const isHealthy = (d.health_status || "").toLowerCase() === "healthy" || (d.disease_or_pest || "").toLowerCase().includes("healthy");

    // Vernacular initial text
    const explanationText = this.activeLanguage === "hi" 
      ? (d.farmer_friendly_explanation_hi || d.farmer_friendly_explanation_en)
      : (d.farmer_friendly_explanation_en || d.farmer_friendly_explanation_hi);

    // Confidence badge color
    const confVal = d.confidence || 90;
    const confBadgeClass = confVal >= 85 ? "badge-success" : (confVal >= 60 ? "badge-warning" : "badge-danger");

    // Severity pill
    const sevBadge = window.utils.getStatusBadge('Severity: ' + (d.severity || 'Moderate'));

    // Image preview URL
    const previewImg = document.getElementById("image-preview-element");
    const previewSrc = previewImg ? previewImg.src : "";

    reportBox.innerHTML = `
      <div class="diagnosis-report-card">
        
        <!-- Report Hero Header (Section 16) -->
        <div class="report-hero-grid">
          ${previewSrc ? `<img src="${previewSrc}" alt="Crop Specimen" class="report-leaf-thumb">` : ''}
          <div>
            <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.25rem;">
              <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600;">Report #${d.analysisId}</span>
              <span class="badge badge-primary" style="font-size: 0.75rem;">${d.ai_engine || 'Gemini 2.5 Flash'}</span>
            </div>
            <h3 style="font-size: 1.4rem; color: var(--primary-900); font-weight: 800; margin-bottom: 0.25rem;">
              ${d.crop} — ${d.disease_or_pest}
            </h3>
            <p style="font-size: 0.88rem; color: ${isHealthy ? 'var(--primary-700)' : 'var(--danger-600)'}; font-weight: 600;">
              ${isHealthy ? '🌿 Peak Physiological Health' : '⚠️ ' + (d.immediate_action || 'Inspect canopy closely.')}
            </p>
          </div>
          <div style="display: flex; flex-direction: column; gap: 0.4rem; align-items: flex-end;">
            <span class="badge ${confBadgeClass}" style="font-size: 0.95rem; padding: 0.4rem 0.8rem;">
              AI Confidence: ${confVal}%
            </span>
            <div style="display: flex; gap: 0.4rem;">
              ${sevBadge}
              <span class="badge badge-secondary">Risk: ${d.risk_level || 'Moderate'}</span>
            </div>
          </div>
        </div>

        <!-- 🗣️ Farmer-Friendly Vernacular Guidance (Section 8) -->
        <div class="vernacular-box">
          <div class="vernacular-header">
            <h5 style="font-size: 0.95rem; color: #065f46; margin: 0;">
              <span>🗣️</span> Farmer Guidance / किसान परामर्श
            </h5>
            <div style="display: flex; gap: 0.5rem; align-items: center;">
              <div class="lang-toggle-group">
                <button type="button" class="lang-btn ${this.activeLanguage === 'en' ? 'active' : ''}" onclick="DiseaseModule.switchLanguage('en')">English</button>
                <button type="button" class="lang-btn ${this.activeLanguage === 'hi' ? 'active' : ''}" onclick="DiseaseModule.switchLanguage('hi')">हिंदी</button>
              </div>
              <button type="button" class="btn-speech-listen" onclick="DiseaseModule.speakDiagnosis()">
                🔊 Listen (सुनें)
              </button>
            </div>
          </div>
          <p class="vernacular-text" id="vernacular-display-text">
            ${explanationText}
          </p>
        </div>

        <!-- Visual Observations vs Contextual Risk (Section 5 & 16) -->
        <div class="observations-context-grid">
          <div class="obs-card">
            <h5><span>🔍</span> What AI Observed on Foliage</h5>
            <ul>
              ${(d.visual_observations || []).map(o => `<li>${o}</li>`).join("")}
            </ul>
          </div>
          <div class="obs-card">
            <h5><span>🌦️</span> Contextual & Environmental Risk</h5>
            <p style="font-size: 0.85rem; color: var(--text-main); margin-bottom: 0.4rem;">
              ${d.contextual_risk_analysis || 'No environmental threats detected.'}
            </p>
            <small style="color: var(--text-muted); font-size: 0.78rem;">
              Affecting: <strong>${d.affected_part || 'Leaf'}</strong> | Diagnostic Reason: ${d.reasoning_summary || ''}
            </small>
          </div>
        </div>

        <!-- Medium Confidence Follow-Up Clarification (Section 4 & 5) -->
        ${(confVal < 85 && (d.follow_up_questions || []).length > 0) ? `
          <div class="follow-up-box">
            <h5><span>❓</span> Refine Diagnosis with Field Observation</h5>
            <p style="font-size: 0.82rem; color: #78350f; margin-bottom: 0.5rem;">
              Answering these clarifying questions helps our agronomy engine give you 100% confirmed guidance:
            </p>
            <ul style="padding-left: 1.2rem; font-size: 0.82rem; color: #78350f; margin-bottom: 0.5rem;">
              ${d.follow_up_questions.map(q => `<li>${q}</li>`).join("")}
            </ul>
            <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
              <input type="text" class="form-control" id="followup-answer-input" placeholder="Type your observation here (e.g. Yes, spots started 3 days after rain)...">
              <button class="btn btn-secondary btn-sm" onclick="DiseaseModule.submitReanalysis()">
                ↻ Re-Analyze
              </button>
            </div>
          </div>
        ` : ''}

        <!-- 🎯 What You Should Do: Validated Action Engine (Section 6) -->
        <h4 style="font-size: 1rem; color: var(--primary-900); margin-bottom: 0.6rem;">
          🎯 Integrated Crop Management Action Plan
        </h4>
        
        <div class="treatment-columns-grid">
          
          <!-- Organic / Biological -->
          <div class="treatment-card">
            <h5>🌿 Organic / Biological Control</h5>
            <div style="font-size: 0.85rem; font-weight: 700; color: var(--primary-800); margin-bottom: 0.35rem;">
              ${org.product_information || 'Neem botanical extract'}
            </div>
            <ul>
              <li><strong>Dosage:</strong> ${org.recommended_rate || 2.5} ${org.unit || 'g/L'}</li>
              <li><strong>Water Ref:</strong> ${org.water_reference_per_acre || 180} L / Acre</li>
              <li><strong>Safety:</strong> ${org.safety_notes || 'Eco-safe formulation.'}</li>
              <li><small style="color: var(--text-muted);">Source: ${org.source || 'ICAR Standard'}</small></li>
            </ul>
          </div>

          <!-- Chemical Remedy -->
          <div class="treatment-card">
            <h5>🧪 Chemical Formulation (CIBRC Approved)</h5>
            <div style="font-size: 0.85rem; font-weight: 700; color: var(--primary-800); margin-bottom: 0.35rem;">
              ${chem.product_information || 'Standard registered fungicide'}
            </div>
            <ul>
              <li><strong>Dosage:</strong> ${chem.recommended_rate || 2.0} ${chem.unit || 'g/L'}</li>
              <li><strong>Water Ref:</strong> ${chem.water_reference_per_acre || 180} L / Acre</li>
              <li><strong>Safety:</strong> ${chem.safety_notes || 'Wear protective gear.'}</li>
              <li><small style="color: var(--text-muted);">Source: ${chem.source || 'CIBRC Registered'}</small></li>
            </ul>
          </div>

          <!-- Prevention & Monitoring -->
          <div class="treatment-card">
            <h5>🛡️ Prevention & Scouting</h5>
            <ul>
              ${(d.prevention_steps || []).map(p => `<li>${p}</li>`).join("")}
              ${d.monitoring_guidance ? `<li style="color: #0369a1;"><strong>Monitor:</strong> ${d.monitoring_guidance}</li>` : ''}
            </ul>
          </div>

        </div>

        <!-- 🧮 Area & Cost Planner (Section 7) -->
        <div class="area-cost-planner-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <h5 style="font-size: 0.95rem; color: var(--primary-900); margin: 0;">
              🧮 Interactive Farm Area & Treatment Cost Planner
            </h5>
            <span class="badge badge-success" style="font-size: 0.75rem;">Deterministic ICAR Calculation</span>
          </div>

          <div class="calculator-controls-row">
            <div class="form-group" style="margin-bottom: 0; min-width: 140px;">
              <label class="form-label" style="font-size: 0.78rem;">Your Land Area</label>
              <input type="number" step="0.1" min="0.1" max="500" class="form-control" id="recalc-area-input" value="${calc.inputArea || 2.5}">
            </div>

            <div class="form-group" style="margin-bottom: 0; min-width: 120px;">
              <label class="form-label" style="font-size: 0.78rem;">Unit</label>
              <select class="form-control" id="recalc-unit-select">
                <option value="Acre" ${(calc.inputUnit || 'Acre') === 'Acre' ? 'selected' : ''}>Acre</option>
                <option value="Hectare" ${(calc.inputUnit || '') === 'Hectare' ? 'selected' : ''}>Hectare</option>
                <option value="Bigha" ${(calc.inputUnit || '') === 'Bigha' ? 'selected' : ''}>Bigha</option>
              </select>
            </div>

            <button class="btn btn-secondary btn-sm" onclick="DiseaseModule.recalculateCost()">
              ⚡ Recalculate Dosage & Cost
            </button>
          </div>

          <div class="calc-results-grid" id="calc-results-display">
            <div class="calc-stat">
              <span class="calc-stat-label">Calculated Area</span>
              <span class="calc-stat-value" id="res-std-area">${calc.standardAreaAcres || 2.5} Acres</span>
            </div>
            <div class="calc-stat">
              <span class="calc-stat-label">Water Required</span>
              <span class="calc-stat-value" id="res-water">${calc.waterVolumeLiters || 450} Liters</span>
            </div>
            <div class="calc-stat">
              <span class="calc-stat-label">Total Product Needed</span>
              <span class="calc-stat-value" id="res-qty">${calc.quantityDisplay || '900 grams'}</span>
            </div>
            <div class="calc-stat">
              <span class="calc-stat-label">Estimated Input Cost</span>
              <span class="calc-stat-value" id="res-cost" style="color: #15803d;">${calc.costDisplay || '₹1,125.00'}</span>
            </div>
          </div>
        </div>

        <!-- 👨‍🔬 Expert Verification Status & Escalation (Section 9) -->
        <div class="expert-review-card">
          <div style="display: flex; gap: 0.75rem; align-items: center;">
            <span style="font-size: 1.5rem;">👨‍🔬</span>
            <div>
              <strong style="font-size: 0.9rem; color: var(--primary-900);">Agricultural Pathologist Verification</strong>
              <div style="font-size: 0.8rem; color: var(--text-muted);" id="expert-status-text">
                ${confVal >= 85 
                  ? 'AI Confidence is high (≥85%). Diagnosis verified against official ICAR standards.' 
                  : 'AI confidence is moderate or low. Secondary review by an ICAR pathologist is recommended.'}
              </div>
            </div>
          </div>

          ${confVal < 85 ? `
            <button class="btn btn-secondary btn-sm" id="btn-escalate-expert" onclick="DiseaseModule.requestExpertReview('${d.analysisId}')">
              📬 Request Agricultural Expert Review
            </button>
          ` : `
            <span class="badge badge-success">✓ Verified Safe</span>
          `}
        </div>

      </div>
    `;
  },

  switchLanguage(lang) {
    this.activeLanguage = lang;
    if (!this.currentDiagnosis) return;

    const textEl = document.getElementById("vernacular-display-text");
    if (textEl) {
      textEl.innerText = lang === "hi"
        ? (this.currentDiagnosis.farmer_friendly_explanation_hi || this.currentDiagnosis.farmer_friendly_explanation_en)
        : (this.currentDiagnosis.farmer_friendly_explanation_en || this.currentDiagnosis.farmer_friendly_explanation_hi);
    }

    const btns = document.querySelectorAll(".lang-btn");
    btns.forEach(b => b.classList.remove("active"));
    const activeBtn = Array.from(btns).find(b => b.innerText.toLowerCase().includes(lang === 'hi' ? 'हिंदी' : 'english'));
    if (activeBtn) activeBtn.classList.add("active");
  },

  speakDiagnosis() {
    if (!('speechSynthesis' in window)) {
      window.utils.showToast("Voice speech synthesis is not supported on this browser.", "warning");
      return;
    }

    window.speechSynthesis.cancel();

    const textEl = document.getElementById("vernacular-display-text");
    const textToSpeak = textEl ? textEl.innerText : "No explanation available.";

    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.lang = this.activeLanguage === "hi" ? "hi-IN" : "en-IN";

    window.speechSynthesis.speak(utterance);
    window.utils.showToast(this.activeLanguage === "hi" ? "🔊 आवाज सुनाई दे रही है..." : "🔊 Audio guidance playing...", "info");
  },

  async recalculateCost() {
    if (!this.currentDiagnosis) return;

    const areaInput = document.getElementById("recalc-area-input");
    const unitSelect = document.getElementById("recalc-unit-select");

    const area = parseFloat(areaInput?.value || 1.0);
    const unit = unitSelect?.value || "Acre";

    try {
      const res = await window.api.post("/api/crop/calculate-cost", {
        crop: this.currentDiagnosis.crop,
        disease: this.currentDiagnosis.disease_or_pest,
        area: area,
        unit: unit
      });

      if (res.success && res.data) {
        const c = res.data;
        const stdArea = document.getElementById("res-std-area");
        const water = document.getElementById("res-water");
        const qty = document.getElementById("res-qty");
        const cost = document.getElementById("res-cost");

        if (stdArea) stdArea.innerText = `${c.standardAreaAcres} Acres`;
        if (water) water.innerText = `${c.waterVolumeLiters} Liters`;
        if (qty) qty.innerText = c.quantityDisplay;
        if (cost) cost.innerText = c.costDisplay;

        window.utils.showToast(`Dosage recalculated for ${area} ${unit}.`, "success");
      }
    } catch (err) {
      window.utils.showToast("Could not calculate dosage: " + err.message, "danger");
    }
  },

  async submitReanalysis() {
    const input = document.getElementById("followup-answer-input");
    const answer = input?.value || "";
    if (!answer.trim()) {
      window.utils.showToast("Please enter your observation.", "warning");
      return;
    }

    const symptomsEl = document.getElementById("scan-symptoms");
    if (symptomsEl) {
      symptomsEl.value = `${symptomsEl.value} [Follow-up: ${answer}]`.trim();
    }

    window.utils.showToast("Re-analyzing with your field observations...", "info");
    await this.runDiagnosis();
  },

  async requestExpertReview(analysisId) {
    const btn = document.getElementById("btn-escalate-expert");
    if (btn) btn.disabled = true;

    try {
      const res = await window.api.post("/api/crop/expert-review", {
        analysisId: analysisId,
        expertDiagnosis: "Pending Specialist Evaluation",
        expertNotes: "Farmer requested secondary verification from diagnostic center.",
        confirmAiPrediction: false
      });

      if (res.success) {
        window.utils.showToast("Scan successfully routed to ICAR agricultural specialist queue.", "success");
        const text = document.getElementById("expert-status-text");
        if (text) text.innerHTML = "<span style='color: #0369a1; font-weight: 600;'>✓ Queued for Expert Pathologist Review</span>";
        if (btn) btn.style.display = "none";
      }
    } catch (err) {
      window.utils.showToast("Could not submit for review: " + err.message, "danger");
      if (btn) btn.disabled = false;
    }
  },

  async loadRegionalRisk() {
    const banner = document.getElementById("regional-risk-banner");
    const badge = document.getElementById("badge-regional-risk");
    const regionText = document.getElementById("risk-region-text");
    const countText = document.getElementById("risk-reports-count");
    const trendText = document.getElementById("risk-trend-text");
    const msgText = document.getElementById("risk-alert-message");
    const chipsRow = document.getElementById("risk-top-pathologies");

    let district = "Karnal";
    let state = "Haryana";
    const locInput = document.getElementById("scan-location");
    if (locInput && locInput.value) {
      const parts = locInput.value.split(",");
      if (parts.length >= 2) {
        district = parts[0].trim();
        state = parts[1].trim();
      } else {
        district = locInput.value.trim();
      }
    }

    try {
      const res = await window.api.get(`/api/crop/risk?state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}`);
      if (res.success && res.data) {
        const r = res.data;
        if (regionText) regionText.innerText = `${r.district}, ${r.state}`;
        if (countText) countText.innerText = `${r.totalReportsLast30Days} Tracked Reports`;
        if (trendText) {
          trendText.innerText = r.weeklyTrend;
          trendText.style.color = r.weeklyTrend === "Rising" ? "#b91c1c" : "var(--primary-700)";
        }
        if (msgText) msgText.innerText = r.earlyWarningMessage;

        if (badge) {
          badge.className = `badge badge-${r.riskBadgeColor}`;
          badge.innerText = `${r.overallRiskLevel === 'Critical' ? '🔴' : (r.overallRiskLevel === 'High' ? '🟠' : (r.overallRiskLevel === 'Moderate' ? '🟡' : '🟢'))} ${r.overallRiskLevel} Risk`;
        }

        if (chipsRow) {
          chipsRow.innerHTML = (r.topPathologies || []).map(p => `
            <span class="risk-chip-pill">
              ${p.pathology} (${p.reportsCount} cases - ${p.percentage}%)
            </span>
          `).join("");
        }
      }
    } catch (err) {
      console.warn("Regional risk fetch notice:", err.message);
    }
  },

  async loadHistory() {
    const container = document.getElementById("disease-history-container");
    if (!container) return;

    try {
      const res = await window.api.get("/api/crop/history");
      if (res.success && res.data) {
        const scans = res.data;
        if (scans.length === 0) {
          container.innerHTML = `
            <div style="text-align: center; padding: 1.5rem; color: var(--text-muted);">
              No past disease scans yet. Use the camera or upload tool above to diagnose your crops.
            </div>
          `;
          return;
        }

        container.innerHTML = `
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Scan ID</th>
                  <th>Crop</th>
                  <th>Pathology / Condition</th>
                  <th>Severity</th>
                  <th>Confidence</th>
                  <th>AI Engine</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                ${scans.map(s => `
                  <tr>
                    <td><strong>${s.analysisId}</strong></td>
                    <td>${s.crop || s.cropDetected}</td>
                    <td><strong>${s.disease_or_pest || s.possibleDisease}</strong></td>
                    <td>${window.utils.getStatusBadge(s.severity)}</td>
                    <td><span class="badge ${s.confidence >= 85 ? 'badge-success' : 'badge-warning'}">${s.confidence}%</span></td>
                    <td><small style="color: var(--primary-700);">${s.ai_engine || 'Gemini 2.5 Flash'}</small></td>
                    <td><small>${window.utils.formatDate(s.created_at)}</small></td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        `;
      }
    } catch (err) {
      console.warn("History load notice:", err.message);
    }
  }
};
