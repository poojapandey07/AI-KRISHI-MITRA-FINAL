/**
 * Module 2: Procurement Management Controller
 */

window.ProcurementModule = {
  initialized: false,
  centresCache: [],
  cropsCache: [],

  STEPS: [
    "Application Submitted",
    "Slot Confirmed",
    "Produce Received",
    "Quality Checked",
    "Procurement Accepted",
    "Payment Initiated"
  ],

  init() {
    this.bindEvents();
    this.loadData();
    this.initialized = true;
  },

  bindEvents() {
    const btnBook = document.getElementById("btn-open-book-slot");
    if (btnBook) {
      btnBook.onclick = () => this.openBookingModal();
    }

    const formBook = document.getElementById("form-book-slot");
    if (formBook) {
      formBook.onsubmit = (e) => this.handleBookSlot(e);
    }

    const cropFilter = document.getElementById("centre-filter-crop");
    if (cropFilter) {
      cropFilter.onchange = () => this.loadCentres(cropFilter.value);
    }
  },

  async loadData() {
    try {
      await Promise.all([
        this.loadCentres(),
        this.loadApplications()
      ]);
    } catch (err) {
      console.error("Error loading procurement data:", err);
    }
  },

  async loadCentres(crop = "") {
    const container = document.getElementById("centres-list-container");
    if (!container) return;
    window.utils.renderLoading(container, "Loading procurement centres...");

    try {
      const endpoint = crop ? `/api/procurement/centres?crop=${encodeURIComponent(crop)}` : "/api/procurement/centres";
      const res = await window.api.get(endpoint);
      if (res.success && res.data) {
        this.centresCache = res.data;
        if (res.data.length === 0) {
          window.utils.renderEmpty(container, "🏪", "No Centres Found", "Try clearing filters to view all available government procurement centres.");
          return;
        }

        container.innerHTML = res.data.map(c => `
          <div class="centre-card">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <h4 class="centre-name">${c.name}</h4>
                ${window.utils.getStatusBadge(c.status)}
              </div>
              <p class="centre-address">📍 ${c.address}</p>
              <div class="centre-crop-tags">
                ${c.availableCrops.map(crop => `<span class="crop-tag">🌾 ${crop}</span>`).join("")}
              </div>
              <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem;">
                ⏰ ${c.schedule} | 🚚 Capacity: ${c.dailyCapacityQuintals.toLocaleString()} Q/day
              </p>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="ProcurementModule.openBookingModal('${c.centreId}')">
              Book at this Centre →
            </button>
          </div>
        `).join("");
      }
    } catch (err) {
      window.utils.renderError(container, err.message, () => this.loadCentres(crop));
    }
  },

  async loadApplications() {
    const container = document.getElementById("applications-list-container");
    const queueCard = document.getElementById("queue-status-content");
    if (!container) return;
    window.utils.renderLoading(container, "Loading procurement applications...");

    try {
      const res = await window.api.get("/api/procurement/applications");
      if (res.success && res.data) {
        const apps = res.data;

        // Render Top Queue Card with the latest active application
        if (queueCard) {
          const activeApp = apps.find(a => a.status !== "Payment Initiated") || apps[0];
          if (activeApp) {
            queueCard.innerHTML = `
              <div class="queue-token-display">
                <div>
                  <span style="font-size: 0.82rem; color: var(--text-muted);">Current Token No.</span>
                  <div class="token-big-badge">${activeApp.tokenNumber}</div>
                  <div style="font-size: 0.85rem; font-weight: 600; color: var(--primary-900); margin-top: 0.35rem;">
                    ${activeApp.centreName}
                  </div>
                </div>
                <div class="queue-stats-row">
                  <div class="queue-stat-item">
                    <span class="queue-stat-val">${activeApp.queuePosition > 0 ? '#' + activeApp.queuePosition : 'Processing'}</span>
                    <span class="queue-stat-lbl">Queue Pos</span>
                  </div>
                  <div class="queue-stat-item">
                    <span class="queue-stat-val">~${activeApp.estimatedWaitMinutes}m</span>
                    <span class="queue-stat-lbl">Est. Wait</span>
                  </div>
                </div>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed var(--border-light); padding-top: 0.5rem; font-size: 0.82rem;">
                <span>🌾 <strong>${activeApp.cropName}</strong> (${activeApp.quantityQuintals} Quintals)</span>
                <span>${window.utils.getStatusBadge(activeApp.status)}</span>
              </div>
            `;
          } else {
            queueCard.innerHTML = `
              <div class="empty-state" style="padding: 1rem;">
                <p style="color: var(--text-muted);">No active bookings. Book a slot below to generate a queue token.</p>
              </div>
            `;
          }
        }

        // Render Applications list
        if (apps.length === 0) {
          window.utils.renderEmpty(container, "📋", "No Procurement Applications", "You have not booked any procurement slots yet. Click 'Book APMC Mandi Slot' to start.");
          return;
        }

        container.innerHTML = apps.map(app => this.renderApplicationCard(app)).join("");
      }
    } catch (err) {
      window.utils.renderError(container, err.message, () => this.loadApplications());
    }
  },

  renderApplicationCard(app) {
    const currentStepIndex = this.STEPS.indexOf(app.status);
    const nextStep = currentStepIndex >= 0 && currentStepIndex < this.STEPS.length - 1 ? this.STEPS[currentStepIndex + 1] : null;

    return `
      <div class="procurement-item-card">
        <div class="procurement-item-header">
          <div class="proc-id-box">
            <h4>${app.centreName}</h4>
            <p>Application ID: <strong>${app.applicationId}</strong> | Procurement ID: <strong>${app.procurementId}</strong></p>
          </div>
          <div style="text-align: right;">
            ${window.utils.getStatusBadge(app.status)}
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">
              Token: <strong>${app.tokenNumber}</strong> | Date: <strong>${window.utils.formatDate(app.bookingDate)}</strong> (${app.timeSlot})
            </div>
          </div>
        </div>

        <div style="font-size: 0.9rem; margin-bottom: 0.75rem;">
          🌾 Crop: <strong>${app.cropName}</strong> ${app.variety ? `(${app.variety})` : ''} | 
          Quantity: <strong>${app.quantityQuintals} Quintals</strong> | 
          Est. Value: <strong>${window.utils.formatCurrency(app.totalAmount || (app.quantityQuintals * (app.ratePerQuintal || 2200)))}</strong>
        </div>

        <!-- Visual 6-Step Timeline -->
        <div class="status-timeline">
          ${this.STEPS.map((step, idx) => {
            let cls = "";
            if (idx < currentStepIndex) cls = "completed";
            else if (idx === currentStepIndex) cls = "active";
            return `
              <div class="timeline-step ${cls}">
                <div class="step-bullet">${idx < currentStepIndex ? "✓" : (idx + 1)}</div>
                <div class="step-label">${step}</div>
              </div>
            `;
          }).join("")}
        </div>

        <!-- Simulation Toolbar -->
        <div class="procurement-simulation-bar">
          <div>
            <span>⚡ Workflow Progression:</span>
            <small style="color: var(--text-muted); margin-left: 0.4rem;">
              ${nextStep ? `Next stage: <strong>${nextStep}</strong>` : 'Full workflow finished! Check Krishi Finance tab.'}
            </small>
          </div>
          ${nextStep ? `
            <button class="btn btn-primary btn-sm" onclick="ProcurementModule.advanceStatus('${app.applicationId}', '${nextStep}')">
              Advance to "${nextStep}" →
            </button>
          ` : `
            <span class="badge badge-success">✓ Payout Routed to Krishi Finance</span>
          `}
        </div>
      </div>
    `;
  },

  async openBookingModal(preselectedCentreId = null) {
    // Populate centres dropdown
    const centreSelect = document.getElementById("book-centre-select");
    if (centreSelect) {
      if (this.centresCache.length === 0) {
        const res = await window.api.get("/api/procurement/centres");
        if (res.success) this.centresCache = res.data;
      }
      centreSelect.innerHTML = `<option value="">-- Choose Mandi / Centre --</option>` +
        this.centresCache.map(c => `
          <option value="${c.centreId}" ${c.centreId === preselectedCentreId ? "selected" : ""}>
            ${c.name} (${c.district}, ${c.state})
          </option>
        `).join("");
    }

    // Populate crops dropdown
    const cropSelect = document.getElementById("book-crop-select");
    if (cropSelect) {
      try {
        const res = await window.api.get("/api/farmers/crops");
        if (res.success && res.data && res.data.length > 0) {
          this.cropsCache = res.data;
          cropSelect.innerHTML = `<option value="">-- Choose Registered Crop --</option>` +
            res.data.map(cr => `
              <option value="${cr.cropId}">${cr.cropName} (${cr.variety || 'Standard'})</option>
            `).join("");
        } else {
          // Fallback if no crops added yet
          cropSelect.innerHTML = `
            <option value="GENERAL_WHEAT">Wheat (गेहूं)</option>
            <option value="GENERAL_MUSTARD">Mustard (सरसों)</option>
            <option value="GENERAL_PADDY">Paddy / Rice (धान)</option>
          `;
        }
      } catch {
        cropSelect.innerHTML = `<option value="GENERAL_WHEAT">Wheat</option>`;
      }
    }

    // Set default date to tomorrow
    const dateInput = document.getElementById("book-date");
    if (dateInput && !dateInput.value) {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      dateInput.value = tomorrow.toISOString().split("T")[0];
    }

    window.utils.openModal("modal-book-slot");
  },

  async handleBookSlot(e) {
    e.preventDefault();
    const centreId = document.getElementById("book-centre-select").value;
    const cropId = document.getElementById("book-crop-select").value;
    const quantityQuintals = parseFloat(document.getElementById("book-quantity").value);
    const bookingDate = document.getElementById("book-date").value;
    const timeSlot = document.getElementById("book-slot-select").value;

    if (!centreId || !cropId) {
      window.utils.showToast("Please choose a centre and crop.", "warning");
      return;
    }

    try {
      const res = await window.api.post("/api/procurement/applications", {
        centreId, cropId, quantityQuintals, bookingDate, timeSlot
      });

      if (res.success && res.data) {
        window.utils.showToast(`Slot confirmed! Token: ${res.data.tokenNumber}`, "success");
        window.utils.closeModal("modal-book-slot");
        document.getElementById("form-book-slot").reset();
        await this.loadApplications();
      }
    } catch (err) {
      window.utils.showToast(err.message, "error");
    }
  },

  async advanceStatus(applicationId, nextStatus) {
    try {
      const res = await window.api.patch(`/api/procurement/applications/${applicationId}/status`, {
        status: nextStatus,
        qualityGrade: nextStatus === "Quality Checked" || nextStatus === "Procurement Accepted" || nextStatus === "Payment Initiated" ? "Grade A (FAQ Passed)" : null,
        moisturePercent: 11.6,
        ratePerQuintal: 2425.0
      });

      if (res.success) {
        if (nextStatus === "Payment Initiated") {
          window.utils.showToast("Procurement Accepted & Payment Initiated! Payout routed to Krishi Finance module.", "success", 5000);
        } else {
          window.utils.showToast(`Application updated to '${nextStatus}'.`, "info");
        }
        await this.loadApplications();
      }
    } catch (err) {
      window.utils.showToast(err.message, "error");
    }
  }
};
