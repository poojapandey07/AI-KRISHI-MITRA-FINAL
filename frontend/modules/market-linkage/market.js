/**
 * Module 6: Market Linkage Controller
 */

window.MarketModule = {
  initialized: false,
  buyersCache: [],

  init() {
    this.bindEvents();
    this.loadData();
    this.initialized = true;
  },

  bindEvents() {
    const btnSearch = document.getElementById("btn-mkt-search");
    const btnReset = document.getElementById("btn-mkt-reset");
    const formConnect = document.getElementById("form-buyer-connect");

    if (btnSearch) {
      btnSearch.onclick = () => {
        const crop = document.getElementById("mkt-search-crop").value;
        const location = document.getElementById("mkt-search-location").value;
        this.loadPrices(crop, location);
      };
    }

    if (btnReset) {
      btnReset.onclick = () => {
        document.getElementById("mkt-search-crop").value = "";
        document.getElementById("mkt-search-location").value = "";
        this.loadPrices();
      };
    }

    if (formConnect) {
      formConnect.onsubmit = (e) => this.handleConnectBuyer(e);
    }
  },

  async loadData() {
    try {
      await Promise.all([
        this.loadPrices(),
        this.loadBuyers(),
        this.loadDashboardSummary()
      ]);
    } catch (err) {
      console.error("Error loading market data:", err);
    }
  },

  async loadPrices(crop = "", location = "") {
    const tbody = document.getElementById("mkt-prices-tbody");
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 2rem;">Loading live mandi rates...</td></tr>`;

    try {
      let url = "/api/market/prices";
      const params = new URLSearchParams();
      if (crop) params.append("crop", crop);
      if (location) params.append("location", location);
      if (params.toString()) url += `?${params.toString()}`;

      const res = await window.api.get(url);
      if (res.success && res.data) {
        const list = res.data;
        if (list.length === 0) {
          tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--text-muted);">No mandi rates found for your search.</td></tr>`;
          return;
        }

        tbody.innerHTML = list.map(p => {
          let trendClass = "trend-flat";
          let trendIcon = "▬";
          if (p.trend === "up") { trendClass = "trend-up"; trendIcon = "▲ " + p.change; }
          else if (p.trend === "down") { trendClass = "trend-down"; trendIcon = "▼ " + p.change; }

          return `
            <tr>
              <td><strong>${p.crop}</strong> <br><small style="color: var(--text-muted);">${p.variety || 'Standard'}</small></td>
              <td>${p.mandi} <br><small style="color: var(--text-muted);">${p.district}</small></td>
              <td>${p.state}</td>
              <td style="font-size: 1.05rem; font-weight: 700; color: var(--primary-900);">
                ${window.utils.formatCurrency(p.modalPrice)}
                <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 400;">/Q</span>
              </td>
              <td><small>${window.utils.formatCurrency(p.minPrice)} - ${window.utils.formatCurrency(p.maxPrice)}</small></td>
              <td><span class="${trendClass}">${trendIcon}</span></td>
            </tr>
          `;
        }).join("");
      }
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--danger-600); padding: 2rem;">Error: ${err.message}</td></tr>`;
    }
  },

  async loadBuyers() {
    const container = document.getElementById("buyers-cards-container");
    if (!container) return;

    window.utils.renderLoading(container, "Loading corporate buyer leads...");

    try {
      const res = await window.api.get("/api/market/buyers");
      if (res.success && res.data) {
        this.buyersCache = res.data;
        const list = res.data;
        if (list.length === 0) {
          window.utils.renderEmpty(container, "🤝", "No Buyers Currently", "Check back soon for new procurement contracts.");
          return;
        }

        container.innerHTML = list.map(b => `
          <div class="buyer-lead-card">
            <div class="buyer-header">
              <span class="buyer-company">${b.companyName}</span>
              ${window.utils.getStatusBadge(b.status)}
            </div>
            <div class="buyer-crop-req">
              🌾 Requirement: <strong>${b.cropRequirement}</strong> (${b.preferredVariety || 'All Varieties'})
            </div>
            <div class="buyer-price-box">
              <span>Indicative Price: <strong style="color: var(--primary-800);">${window.utils.formatCurrency(b.indicativePrice)}/Q</strong></span>
              <span style="font-size: 0.8rem; color: var(--text-muted);">Qty: <strong>${b.requiredQuantity}</strong></span>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.75rem;">
              📍 ${b.location} <br>
              💳 Terms: ${b.paymentTerms || 'Standard Bank Transfer'}
            </div>
            <button class="btn btn-primary btn-sm" style="width: 100%;" onclick="MarketModule.openConnectModal('${b.buyerId}')">
              Connect & Sell Produce →
            </button>
          </div>
        `).join("");
      }
    } catch (err) {
      window.utils.renderError(container, err.message, () => this.loadBuyers());
    }
  },

  openConnectModal(buyerId) {
    const buyer = this.buyersCache.find(b => b.buyerId === buyerId);
    if (!buyer) return;

    document.getElementById("connect-buyer-id").value = buyerId;
    const briefBox = document.getElementById("modal-buyer-brief");
    if (briefBox) {
      briefBox.innerHTML = `
        <h4 style="font-size: 1.05rem; color: var(--primary-900);">${buyer.companyName}</h4>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin: 0.2rem 0 0.5rem 0;">
          Buyer Category: <strong>${buyer.category}</strong> | Indicative: <strong>${window.utils.formatCurrency(buyer.indicativePrice)}/Q</strong>
        </p>
        <div style="font-size: 0.82rem; color: var(--text-dark);">
          <strong>Quality Specs:</strong> ${buyer.qualitySpecifications || 'Agmark Grade 1 standard produce.'}
        </div>
      `;
    }

    const expPriceInput = document.getElementById("connect-expected-price");
    if (expPriceInput) expPriceInput.value = buyer.indicativePrice;

    window.utils.openModal("modal-buyer-connect");
  },

  async handleConnectBuyer(e) {
    e.preventDefault();
    const buyerId = document.getElementById("connect-buyer-id").value;
    const quantityOfferedQuintals = parseFloat(document.getElementById("connect-offered-qty").value);
    const expectedPriceInput = document.getElementById("connect-expected-price").value;
    const expectedPricePerQuintal = expectedPriceInput ? parseFloat(expectedPriceInput) : null;
    const farmerNote = document.getElementById("connect-note").value;

    try {
      const res = await window.api.post(`/api/market/buyers/${buyerId}/connect`, {
        quantityOfferedQuintals, expectedPricePerQuintal, farmerNote
      });

      if (res.success && res.data) {
        window.utils.showToast(res.data.message, "success", 6000);
        window.utils.closeModal("modal-buyer-connect");
        document.getElementById("form-buyer-connect").reset();
      }
    } catch (err) {
      window.utils.showToast(err.message, "error");
    }
  },

  async loadDashboardSummary() {
    try {
      const res = await window.api.get("/api/market/dashboard");
      if (res.success && res.data) {
        const d = res.data;
        const countEl = document.getElementById("stat-mandis-count");
        if (countEl) countEl.textContent = d.totalMandisCovered;
      }
    } catch (err) {
      console.warn("Dashboard summary note:", err.message);
    }
  }
};
