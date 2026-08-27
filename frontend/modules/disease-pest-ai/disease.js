/**
 * Module 5: Disease & Pest AI Controller
 */

window.DiseaseModule = {
  initialized: false,
  selectedFile: null,

  init() {
    this.bindEvents();
    this.loadHistory();
    this.initialized = true;
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

  async runSampleTest(sampleName) {
    // Generate a lightweight canvas image blob representing the crop sample
    const canvas = document.createElement("canvas");
    canvas.width = 400;
    canvas.height = 300;
    const ctx = canvas.getContext("2d");
    
    // Draw leaf-like background
    ctx.fillStyle = sampleName.includes("Healthy") ? "#2e7d32" : "#854d0e";
    ctx.fillRect(0, 0, 400, 300);
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 20px sans-serif";
    ctx.fillText(`AI Krishi Sample: ${sampleName}`, 20, 150);

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
    const laserLine = document.getElementById("scanner-laser-line");
    const btnRun = document.getElementById("btn-run-diagnosis");

    if (laserLine) laserLine.style.display = "block";
    if (btnRun) btnRun.disabled = true;
    if (reportBox) {
      reportBox.style.display = "block";
      window.utils.renderLoading(reportBox, "Executing computer vision feature extraction & pathology diagnosis...");
    }

    const formData = new FormData();
    formData.append("file", this.selectedFile);

    try {
      const res = await window.api.post("/api/disease-analysis", formData);
      if (res.success && res.data) {
        const d = res.data;
        this.renderDiagnosisReport(d);
        await this.loadHistory();
      }
    } catch (err) {
      if (reportBox) {
        window.utils.renderError(reportBox, err.message, () => this.runDiagnosis());
      }
    } finally {
      if (laserLine) laserLine.style.display = "none";
      if (btnRun) btnRun.disabled = false;
    }
  },

  renderDiagnosisReport(d) {
    const reportBox = document.getElementById("disease-diagnosis-report");
    if (!reportBox) return;

    const action = d.recommendedAction || {};

    reportBox.innerHTML = `
      <div class="diagnosis-report-card">
        <div class="diagnosis-header">
          <div>
            <span style="font-size: 0.8rem; color: var(--text-muted);">Diagnosis Diagnostic Report #${d.analysisId}</span>
            <h3 style="font-size: 1.35rem; color: var(--primary-900); font-weight: 800;">
              ${d.cropDetected} — ${d.possibleDisease}
            </h3>
            <p style="font-size: 0.88rem; color: var(--danger-600); font-weight: 600; margin-top: 0.2rem;">
              ⚠️ ${action.urgencyText || 'Observe crop canopy closely.'}
            </p>
          </div>
          <div style="text-align: right;">
            <div style="display: flex; gap: 0.5rem; justify-content: flex-end; align-items: center;">
              ${window.utils.getStatusBadge('Severity: ' + d.severity)}
              <span class="badge badge-primary">${d.confidence}% Confidence</span>
            </div>
          </div>
        </div>

        <div style="margin-bottom: 1rem;">
          <h5 style="font-size: 0.9rem; color: var(--primary-900); margin-bottom: 0.35rem;">🔍 Clinical Symptoms Identified:</h5>
          <ul style="padding-left: 1.2rem; font-size: 0.85rem; color: var(--text-dark);">
            ${d.symptoms.map(s => `<li>${s}</li>`).join("")}
          </ul>
        </div>

        <h5 style="font-size: 0.95rem; color: var(--primary-900); margin-bottom: 0.5rem;">💊 Integrated Pest & Disease Management Prescription</h5>
        <div class="treatment-columns-grid">
          
          <div class="treatment-card">
            <h5>🌿 Organic / Biological</h5>
            <ul>
              ${(action.organicTreatment || []).map(t => `<li>${t}</li>`).join("")}
            </ul>
          </div>

          <div class="treatment-card">
            <h5>🧪 Chemical Remedy</h5>
            <ul>
              ${(action.chemicalRemedy || []).map(t => `<li>${t}</li>`).join("")}
            </ul>
          </div>

          <div class="treatment-card">
            <h5>🛡️ Prevention & Agronomy</h5>
            <ul>
              ${(action.preventiveMeasures || []).map(t => `<li>${t}</li>`).join("")}
            </ul>
          </div>

        </div>
      </div>
    `;
  },

  async loadHistory() {
    const container = document.getElementById("disease-history-container");
    if (!container) return;

    try {
      const res = await window.api.get("/api/disease-analysis/history");
      if (res.success && res.data) {
        const scans = res.data;
        if (scans.length === 0) {
          container.innerHTML = `
            <div style="text-align: center; padding: 1.5rem; color: var(--text-muted);">
              No past disease scans yet. Use the camera tool above to diagnose your crops.
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
                  <th>Diagnosed Pathology</th>
                  <th>Severity</th>
                  <th>Confidence</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                ${scans.map(s => `
                  <tr>
                    <td><strong>${s.analysisId}</strong></td>
                    <td>${s.cropDetected}</td>
                    <td><strong>${s.possibleDisease}</strong></td>
                    <td>${window.utils.getStatusBadge(s.severity)}</td>
                    <td>${s.confidence}%</td>
                    <td><small>${window.utils.formatDate(s.created_at)}</small></td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        `;
      }
    } catch (err) {
      console.warn("History load note:", err.message);
    }
  }
};
