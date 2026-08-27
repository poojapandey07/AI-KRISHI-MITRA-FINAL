/**
 * Module 4: AI Standards & Recommendation Controller
 */

window.AIStandardsModule = {
  initialized: false,

  init() {
    this.bindEvents();
    this.loadRecommendations();
    this.initialized = true;
  },

  bindEvents() {
    const form = document.getElementById("form-check-standards");
    if (form) {
      form.onsubmit = (e) => this.handleCheckStandards(e);
    }
  },

  async handleCheckStandards(e) {
    e.preventDefault();
    const crop = document.getElementById("ai-std-crop").value;
    const variety = document.getElementById("ai-std-variety").value;
    const moisturePercent = parseFloat(document.getElementById("ai-std-moisture").value);
    const foreignMatterPercent = parseFloat(document.getElementById("ai-std-foreign").value);
    const damagedGrainsPercent = parseFloat(document.getElementById("ai-std-damaged").value);

    const resultBox = document.getElementById("standards-result-container");
    if (!resultBox) return;

    resultBox.style.display = "block";
    window.utils.renderLoading(resultBox, "Analyzing crop against FCI & Agmark standard thresholds...");

    try {
      const res = await window.api.post("/api/ai/standards", {
        crop, variety, moisturePercent, foreignMatterPercent, damagedGrainsPercent
      });

      if (res.success && res.data) {
        const d = res.data;
        resultBox.innerHTML = `
          <div class="standards-result-box">
            <div class="grade-score-header">
              <div>
                <span style="font-size: 0.8rem; color: var(--text-muted);">Assigned FCI / Agmark Standard</span>
                <div class="grade-big-badge">
                  <span>🏅</span> ${d.assignedGrade}
                </div>
                <p style="font-size: 0.85rem; color: var(--primary-700); margin-top: 0.25rem;">
                  ${d.priceImpactText}
                </p>
              </div>
              <div style="display: flex; align-items: center; gap: 1rem;">
                <div class="score-circle">
                  <span>${d.qualityScore}</span>
                  <small>SCORE</small>
                </div>
                ${window.utils.getStatusBadge(d.isProcurementEligible ? "Procurement Eligible" : "Action Required")}
              </div>
            </div>

            <!-- Parameters Table -->
            <h5 style="font-size: 0.92rem; color: var(--primary-900); margin-bottom: 0.4rem;">Quality Parameter Comparison</h5>
            <div class="table-responsive">
              <table class="param-comparison-table">
                <thead>
                  <tr>
                    <th>Quality Parameter</th>
                    <th>Your Reading</th>
                    <th>FCI Max Allowed</th>
                    <th>Status</th>
                    <th>Action Recommendation</th>
                  </tr>
                </thead>
                <tbody>
                  ${d.comparisons.map(c => `
                    <tr>
                      <td><strong>${c.parameter}</strong></td>
                      <td>${c.farmerValue} ${c.unit}</td>
                      <td>&le; ${c.maxAllowedFCI} ${c.unit}</td>
                      <td>${window.utils.getStatusBadge(c.status)}</td>
                      <td><small>${c.recommendation}</small></td>
                    </tr>
                  `).join("")}
                </tbody>
              </table>
            </div>

            <!-- Agronomy & Storage Advice -->
            <div class="advice-sections-grid">
              <div class="advice-box">
                <h5>🚜 Handling & Drying Technique</h5>
                <p style="font-size: 0.82rem; margin-bottom: 0.5rem; color: var(--text-dark);">
                  <strong>Solar Technique:</strong> ${d.dryingTechnique}
                </p>
                <ul>
                  ${d.handlingAdvice.map(h => `<li>${h}</li>`).join("")}
                </ul>
              </div>
              <div class="advice-box">
                <h5>🛖 Godown & Storage Specifications</h5>
                <ul>
                  ${d.storageAdvice.map(s => `<li>${s}</li>`).join("")}
                </ul>
              </div>
            </div>
          </div>
        `;
      }
    } catch (err) {
      window.utils.renderError(resultBox, err.message, () => this.handleCheckStandards(e));
    }
  },

  async loadRecommendations() {
    const container = document.getElementById("recommendations-container");
    if (!container) return;
    window.utils.renderLoading(container, "Generating tailored AI agricultural advice...");

    try {
      const res = await window.api.get("/api/ai/recommendations");
      if (res.success && res.data) {
        const recs = res.data;
        if (recs.length === 0) {
          window.utils.renderEmpty(container, "💡", "No Recommendations", "Register crops in My Farm to generate tailored AI agronomy tips.");
          return;
        }

        container.innerHTML = recs.map(r => `
          <div class="recommendation-card">
            <div>
              <div class="rec-header">
                <span class="rec-category-tag">🌱 ${r.crop} • ${r.category}</span>
                ${window.utils.getStatusBadge(r.priority + ' Priority')}
              </div>
              <h4 class="rec-title">${r.title}</h4>
              <p class="rec-summary">${r.summary}</p>
            </div>
            <div class="rec-steps">
              <strong>Recommended Action Steps:</strong>
              <ul>
                ${r.actionSteps.map(step => `<li>${step}</li>`).join("")}
              </ul>
            </div>
          </div>
        `).join("");
      }
    } catch (err) {
      window.utils.renderError(container, err.message, () => this.loadRecommendations());
    }
  }
};
