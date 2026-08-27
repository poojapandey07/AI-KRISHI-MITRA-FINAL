/**
 * Module 1: Farmer & Authentication Controller
 */

window.FarmerModule = {
  initialized: false,

  init() {
    this.bindEvents();
    this.loadFarmerData();
    this.initialized = true;
  },

  bindEvents() {
    const btnAddLand = document.getElementById("btn-open-add-land");
    if (btnAddLand) {
      btnAddLand.onclick = () => window.utils.openModal("modal-add-land");
    }

    const btnAddCrop = document.getElementById("btn-open-add-crop");
    if (btnAddCrop) {
      btnAddCrop.onclick = () => window.utils.openModal("modal-add-crop");
    }

    const formAddLand = document.getElementById("form-add-land");
    if (formAddLand) {
      formAddLand.onsubmit = (e) => this.handleAddLand(e);
    }

    const formAddCrop = document.getElementById("form-add-crop");
    if (formAddCrop) {
      formAddCrop.onsubmit = (e) => this.handleAddCrop(e);
    }
  },

  async loadFarmerData() {
    try {
      await Promise.all([
        this.loadProfile(),
        this.loadLand(),
        this.loadCrops()
      ]);
    } catch (err) {
      console.error("Error loading farmer module data:", err);
    }
  },

  async loadProfile() {
    try {
      const res = await window.api.get("/api/farmers/profile");
      if (res.success && res.data) {
        const p = res.data;
        const nameEl = document.getElementById("profile-display-name");
        const locEl = document.getElementById("profile-display-location");
        const mobEl = document.getElementById("profile-display-mobile");
        const emailEl = document.getElementById("profile-display-email");
        const idBadge = document.getElementById("profile-badge-id");
        const avatarLetter = document.getElementById("profile-avatar-letter");
        const statLand = document.getElementById("profile-stat-land");
        const statCrops = document.getElementById("profile-stat-crops");

        if (nameEl) nameEl.textContent = p.fullName;
        if (locEl) locEl.textContent = `${p.village}, ${p.district}, ${p.state}`;
        if (mobEl) mobEl.textContent = p.mobile;
        if (emailEl) emailEl.textContent = p.email || "No email linked";
        if (idBadge) idBadge.textContent = p.farmerId;
        if (avatarLetter) avatarLetter.textContent = window.utils.getInitials(p.fullName);
        if (statLand) statLand.textContent = p.totalLandAcres;
        if (statCrops) statCrops.textContent = p.totalCropsCount;

        // Also update header user card
        const topFarmerName = document.getElementById("top-farmer-name");
        const topFarmerId = document.getElementById("top-farmer-id");
        const topUserInitials = document.getElementById("top-user-initials");
        if (topFarmerName) topFarmerName.textContent = p.fullName;
        if (topFarmerId) topFarmerId.textContent = p.farmerId;
        if (topUserInitials) topUserInitials.textContent = window.utils.getInitials(p.fullName);
      }
    } catch (err) {
      console.error("Failed to load profile:", err);
    }
  },

  async loadLand() {
    const container = document.getElementById("land-list-container");
    if (!container) return;
    window.utils.renderLoading(container, "Loading land records...");

    try {
      const res = await window.api.get("/api/farmers/land");
      if (res.success && res.data) {
        const list = res.data;
        if (list.length === 0) {
          window.utils.renderEmpty(container, "🏞️", "No Land Registered Yet", "Add your first land parcel to receive tailored crop & procurement recommendations.");
          return;
        }

        container.innerHTML = list.map(item => `
          <div class="asset-item-card">
            <div class="asset-main-info">
              <h4>${item.location}</h4>
              <div class="asset-sub-info">
                <span>🌱 Soil: <strong>${item.soilType}</strong></span>
                <span>💧 Irrigation: <strong>${item.irrigationType}</strong></span>
              </div>
            </div>
            <div class="asset-area-pill">
              ${item.area} ${item.unit}
            </div>
          </div>
        `).join("");
      }
    } catch (err) {
      window.utils.renderError(container, err.message, () => this.loadLand());
    }
  },

  async loadCrops() {
    const container = document.getElementById("crops-list-container");
    if (!container) return;
    window.utils.renderLoading(container, "Loading crop records...");

    try {
      const res = await window.api.get("/api/farmers/crops");
      if (res.success && res.data) {
        const list = res.data;
        if (list.length === 0) {
          window.utils.renderEmpty(container, "🌾", "No Crops Added", "Register your current crops to track procurement slots and AI health checks.");
          return;
        }

        container.innerHTML = list.map(item => `
          <div class="asset-item-card">
            <div class="asset-main-info">
              <h4>${item.cropName} <small style="font-weight: 500; color: var(--primary-700);">(${item.variety})</small></h4>
              <div class="asset-sub-info">
                <span>📅 Sown: <strong>${window.utils.formatDate(item.sowingDate)}</strong></span>
                <span>🌾 Harvest: <strong>${window.utils.formatDate(item.expectedHarvest)}</strong></span>
                ${item.estimatedYieldQuintals ? `<span>⚖️ Est: <strong>${item.estimatedYieldQuintals} Q</strong></span>` : ''}
              </div>
            </div>
            <div class="asset-area-pill">
              ${item.cultivatedArea} ${item.areaUnit || 'Acres'}
            </div>
          </div>
        `).join("");
      }
    } catch (err) {
      window.utils.renderError(container, err.message, () => this.loadCrops());
    }
  },

  async handleAddLand(e) {
    e.preventDefault();
    const area = parseFloat(document.getElementById("land-area").value);
    const unit = document.getElementById("land-unit").value;
    const soilType = document.getElementById("land-soil").value;
    const irrigationType = document.getElementById("land-irrigation").value;
    const location = document.getElementById("land-location").value;

    try {
      const res = await window.api.post("/api/farmers/land", {
        area, unit, soilType, irrigationType, location
      });
      if (res.success) {
        window.utils.showToast("Land parcel added successfully!", "success");
        window.utils.closeModal("modal-add-land");
        document.getElementById("form-add-land").reset();
        await this.loadFarmerData();
      }
    } catch (err) {
      window.utils.showToast(err.message, "error");
    }
  },

  async handleAddCrop(e) {
    e.preventDefault();
    const cropName = document.getElementById("crop-name").value;
    const variety = document.getElementById("crop-variety").value;
    const sowingDate = document.getElementById("crop-sowing").value;
    const expectedHarvest = document.getElementById("crop-harvest").value;
    const cultivatedArea = parseFloat(document.getElementById("crop-area").value);
    const yieldInput = document.getElementById("crop-yield").value;
    const estimatedYieldQuintals = yieldInput ? parseFloat(yieldInput) : null;

    try {
      const res = await window.api.post("/api/farmers/crops", {
        cropName, variety, sowingDate, expectedHarvest,
        cultivatedArea, areaUnit: "Acres", estimatedYieldQuintals
      });
      if (res.success) {
        window.utils.showToast("Crop registered successfully!", "success");
        window.utils.closeModal("modal-add-crop");
        document.getElementById("form-add-crop").reset();
        await this.loadFarmerData();
      }
    } catch (err) {
      window.utils.showToast(err.message, "error");
    }
  }
};
