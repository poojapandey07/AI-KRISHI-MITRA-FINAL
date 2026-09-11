/**
 * AI Krishi Mitra — Master Application Coordinator
 * Manages modular view routing, unified dashboard data aggregation, and auth lifecycle.
 */

class AppRouter {
  constructor() {
    this.currentView = "dashboard";
    this.views = {
      dashboard: document.getElementById("view-dashboard"),
      farmer: document.getElementById("view-farmer"),
      procurement: document.getElementById("view-procurement"),
      finance: document.getElementById("view-finance"),
      "ai-standards": document.getElementById("view-ai-standards"),
      "disease-pest-ai": document.getElementById("view-disease-pest-ai"),
      "market-linkage": document.getElementById("view-market-linkage")
    };
  }

  init() {
    this.bindGlobalEvents();
    this.checkAuthAndStart();
  }

  bindGlobalEvents() {
    // Navigation items
    document.querySelectorAll(".nav-item[data-view]").forEach(item => {
      item.addEventListener("click", () => {
        const view = item.getAttribute("data-view");
        this.navigate(view);
        this.closeMobileSidebar();
      });
    });

    // Mobile Sidebar
    const mobileBtn = document.getElementById("mobile-menu-btn");
    const sidebar = document.getElementById("app-sidebar");
    const backdrop = document.getElementById("sidebar-backdrop");

    if (mobileBtn && sidebar && backdrop) {
      mobileBtn.onclick = () => {
        sidebar.classList.add("mobile-open");
        backdrop.classList.add("active");
      };
      backdrop.onclick = () => this.closeMobileSidebar();
    }

    // Logout
    const btnLogout = document.getElementById("btn-logout");
    if (btnLogout) {
      btnLogout.onclick = () => window.auth.logout();
    }

    // Auth Modal Forms
    const formLogin = document.getElementById("form-auth-login");
    if (formLogin) {
      formLogin.onsubmit = (e) => this.handleLogin(e);
    }

    const formRegister = document.getElementById("form-auth-register");
    if (formRegister) {
      formRegister.onsubmit = (e) => this.handleRegister(e);
    }

    // Demo Fill button & Dropdown change
    const btnFillDemo = document.getElementById("btn-fill-demo");
    const demoSelector = document.getElementById("demo-account-selector");
    
    const fillSelectedDemo = () => {
      const selectedMobile = demoSelector ? demoSelector.value : "9876543210";
      const mobileInput = document.getElementById("login-mobile");
      const passInput = document.getElementById("login-password");
      if (mobileInput) mobileInput.value = selectedMobile;
      if (passInput) passInput.value = "Password@123";
    };

    if (btnFillDemo) {
      btnFillDemo.onclick = fillSelectedDemo;
    }
    if (demoSelector) {
      demoSelector.onchange = fillSelectedDemo;
    }

    // Listen to auth events
    window.addEventListener("auth:change", (e) => {
      if (e.detail.isAuthenticated) {
        this.hideAuthPage();
        this.updateHeaderUserInfo(e.detail.farmer);
        this.navigate("dashboard");
      } else {
        this.showAuthPage();
      }
    });

    window.addEventListener("auth:expired", () => {
      window.utils.showToast("Your session has expired. Please log in again.", "warning");
      this.showAuthPage();
    });
  }

  closeMobileSidebar() {
    const sidebar = document.getElementById("app-sidebar");
    const backdrop = document.getElementById("sidebar-backdrop");
    if (sidebar) sidebar.classList.remove("mobile-open");
    if (backdrop) backdrop.classList.remove("active");
  }

  checkAuthAndStart() {
    if (window.auth.isAuthenticated()) {
      const farmer = window.auth.getFarmer();
      this.hideAuthPage();
      this.updateHeaderUserInfo(farmer);
      this.navigate("dashboard");
    } else {
      this.showAuthPage();
    }
  }

  showAuthPage() {
    const loginPage = document.getElementById("view-login-page");
    const appContainer = document.getElementById("app-container");
    if (loginPage) loginPage.style.display = "flex";
    if (appContainer) appContainer.style.display = "none";
  }

  hideAuthPage() {
    const loginPage = document.getElementById("view-login-page");
    const appContainer = document.getElementById("app-container");
    if (loginPage) loginPage.style.display = "none";
    if (appContainer) appContainer.style.display = "flex";
  }

  showAuthModal() {
    this.showAuthPage();
  }

  switchAuthTab(tab) {
    const tabLogin = document.getElementById("tab-auth-login");
    const tabReg = document.getElementById("tab-auth-register");
    const paneLogin = document.getElementById("pane-auth-login");
    const paneReg = document.getElementById("pane-auth-register");

    if (tab === "login") {
      tabLogin.classList.add("active");
      tabReg.classList.remove("active");
      paneLogin.style.display = "block";
      paneReg.style.display = "none";
    } else {
      tabLogin.classList.remove("active");
      tabReg.classList.add("active");
      paneLogin.style.display = "none";
      paneReg.style.display = "block";
    }
  }

  async handleLogin(e) {
    e.preventDefault();
    const mobileOrEmail = document.getElementById("login-mobile").value;
    const password = document.getElementById("login-password").value;

    try {
      await window.auth.login(mobileOrEmail, password);
      window.utils.showToast("Welcome back to AI Krishi Mitra!", "success");
    } catch (err) {
      window.utils.showToast(err.message, "error");
    }
  }

  async handleRegister(e) {
    e.preventDefault();
    const fullName = document.getElementById("reg-name").value;
    const mobile = document.getElementById("reg-mobile").value;
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;
    const state = document.getElementById("reg-state").value;
    const district = document.getElementById("reg-district").value;
    const village = document.getElementById("reg-village").value;

    try {
      await window.auth.register({
        fullName, mobile, email: email || null, password, state, district, village
      });
      window.utils.showToast("Account created successfully! Welcome to AI Krishi Mitra.", "success");
    } catch (err) {
      window.utils.showToast(err.message, "error");
    }
  }

  updateHeaderUserInfo(farmer) {
    if (!farmer) return;
    const nameEl = document.getElementById("top-farmer-name");
    const idEl = document.getElementById("top-farmer-id");
    const initialsEl = document.getElementById("top-user-initials");

    if (nameEl) nameEl.textContent = farmer.fullName;
    if (idEl) idEl.textContent = farmer.farmerId;
    if (initialsEl) initialsEl.textContent = window.utils.getInitials(farmer.fullName);
  }

  navigate(viewName) {
    // Update nav active classes
    document.querySelectorAll(".nav-item").forEach(item => {
      if (item.getAttribute("data-view") === viewName) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });

    // Update view container visibility
    Object.keys(this.views).forEach(key => {
      const container = this.views[key];
      if (container) {
        if (key === viewName) {
          container.style.display = "block";
        } else {
          container.style.display = "none";
        }
      }
    });

    this.currentView = viewName;

    // Update Header Title
    const titleEl = document.getElementById("current-page-title");
    const subTitleEl = document.getElementById("current-page-subtitle");
    const titles = {
      dashboard: { title: "Farmer Dashboard", sub: "Unified overview of your farm, procurement, finance & markets" },
      farmer: { title: "My Farm & Profile", sub: "Manage your registered land parcels and cultivated crops" },
      procurement: { title: "Procurement Management", sub: "Book mandi slots, view real-time queue tokens & track produce" },
      finance: { title: "Krishi Finance", sub: "Bank account linking, sandbox verification & direct DBT settlements" },
      "ai-standards": { title: "AI Standards & Recommendations", sub: "FCI/Agmark crop grading and personalized agronomy tips" },
      "disease-pest-ai": { title: "Crop Health & Disease AI", sub: "Instant AI diagnostics & pest treatment prescriptions" },
      "market-linkage": { title: "Market Linkage & APMC Prices", sub: "Live Mandi spot prices and verified corporate buyer opportunities" }
    };

    if (titles[viewName]) {
      if (titleEl) titleEl.textContent = titles[viewName].title;
      if (subTitleEl) subTitleEl.textContent = titles[viewName].sub;
    }

    // Trigger module controller initialization
    if (viewName === "dashboard") {
      this.loadUnifiedDashboard();
    } else if (viewName === "farmer" && window.FarmerModule) {
      window.FarmerModule.init();
    } else if (viewName === "procurement" && window.ProcurementModule) {
      window.ProcurementModule.init();
    } else if (viewName === "finance" && window.FinanceModule) {
      window.FinanceModule.init();
    } else if (viewName === "ai-standards" && window.AIStandardsModule) {
      window.AIStandardsModule.init();
    } else if (viewName === "disease-pest-ai" && window.DiseaseModule) {
      window.DiseaseModule.init();
    } else if (viewName === "market-linkage" && window.MarketModule) {
      window.MarketModule.init();
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async loadUnifiedDashboard() {
    try {
      // 1. Load Farmer Profile Card
      const profRes = await window.api.get("/api/farmers/profile").catch(() => null);
      if (profRes && profRes.data) {
        const p = profRes.data;
        const dashName = document.getElementById("dash-farmer-name");
        const dashLand = document.getElementById("dash-land-val");
        const dashCrops = document.getElementById("dash-crops-val");
        if (dashName) dashName.textContent = p.fullName;
        if (dashLand) dashLand.textContent = `${p.totalLandAcres} Acres`;
        if (dashCrops) dashCrops.textContent = `${p.totalCropsCount} Registered`;
      }

      // 2. Load Procurement Summary
      const procRes = await window.api.get("/api/procurement/applications").catch(() => null);
      if (procRes && procRes.data && procRes.data.length > 0) {
        const active = procRes.data[0];
        const statusEl = document.getElementById("dash-proc-status");
        const tokenEl = document.getElementById("dash-proc-token");
        const queueEl = document.getElementById("dash-proc-queue");
        if (statusEl) statusEl.innerHTML = window.utils.getStatusBadge(active.status);
        if (tokenEl) tokenEl.textContent = active.tokenNumber;
        if (queueEl) queueEl.textContent = active.queuePosition > 0 ? `#${active.queuePosition} in Queue` : 'Processing';
      }

      // 3. Load Finance Summary
      const bankRes = await window.api.get("/api/finance/bank").catch(() => null);
      const payRes = await window.api.get("/api/finance/payments").catch(() => null);
      if (bankRes && bankRes.data) {
        const bankBadge = document.getElementById("dash-bank-badge");
        if (bankBadge) bankBadge.innerHTML = window.utils.getStatusBadge(bankRes.data.verificationStatus);
      }
      if (payRes && payRes.data && payRes.data.length > 0) {
        const latestPay = payRes.data[0];
        const payValEl = document.getElementById("dash-latest-payout-val");
        const payStatusEl = document.getElementById("dash-latest-payout-status");
        if (payValEl) payValEl.textContent = window.utils.formatCurrency(latestPay.amount);
        if (payStatusEl) payStatusEl.innerHTML = window.utils.getStatusBadge(latestPay.status);
      }

      // 4. Load AI Advice Headline
      const aiRes = await window.api.get("/api/ai/recommendations").catch(() => null);
      if (aiRes && aiRes.data && aiRes.data.length > 0) {
        const topTip = aiRes.data[0];
        const aiTipTitle = document.getElementById("dash-ai-tip-title");
        const aiTipCrop = document.getElementById("dash-ai-tip-crop");
        if (aiTipTitle) aiTipTitle.textContent = topTip.title;
        if (aiTipCrop) aiTipCrop.textContent = `${topTip.crop} • ${topTip.category}`;
      }

      // 5. Load Crop Health Scanner summary
      const disRes = await window.api.get("/api/disease-analysis/history").catch(() => null);
      if (disRes && disRes.data && disRes.data.length > 0) {
        const lastScan = disRes.data[0];
        const scanName = document.getElementById("dash-scan-disease");
        const scanSeverity = document.getElementById("dash-scan-severity");
        if (scanName) scanName.textContent = `${lastScan.cropDetected}: ${lastScan.possibleDisease}`;
        if (scanSeverity) scanSeverity.innerHTML = window.utils.getStatusBadge(lastScan.severity);
      }

      // 6. Load Live Mandi Prices for Dashboard Ticker
      const mktRes = await window.api.get("/api/market/dashboard").catch(() => null);
      if (mktRes && mktRes.data && mktRes.data.farmerCropPrices) {
        const tickerContainer = document.getElementById("dash-mandi-ticker");
        if (tickerContainer) {
          tickerContainer.innerHTML = mktRes.data.farmerCropPrices.slice(0, 3).map(p => `
            <div class="dash-price-pill">
              <strong>${p.crop}</strong> (${p.mandi}): 
              <span style="color: var(--primary-700); font-weight: 700;">${window.utils.formatCurrency(p.modalPrice)}/Q</span>
            </div>
          `).join("");
        }
      }

    } catch (err) {
      console.warn("Unified dashboard load note:", err.message);
    }
  }
}

// Global router initialization
document.addEventListener("DOMContentLoaded", () => {
  window.appRouter = new AppRouter();
  window.appRouter.init();
});
