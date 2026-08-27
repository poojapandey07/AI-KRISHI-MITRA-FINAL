/**
 * Utility functions for AI Krishi Mitra
 */

window.utils = {
  // Toast Notification System
  showToast(message, type = "success", duration = 4000) {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let icon = "✓";
    if (type === "error") icon = "✕";
    if (type === "warning") icon = "⚠";
    if (type === "info") icon = "ℹ";

    toast.innerHTML = `
      <span style="font-weight: 700; font-size: 1.1rem;">${icon}</span>
      <div style="flex: 1;">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  // Currency Formatter
  formatCurrency(amount) {
    if (amount === undefined || amount === null || isNaN(amount)) return "₹0";
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0
    }).format(amount);
  },

  // Date Formatter
  formatDate(dateStr) {
    if (!dateStr) return "-";
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric"
      });
    } catch {
      return dateStr;
    }
  },

  // Status Badge Generator
  getStatusBadge(status) {
    if (!status) return `<span class="badge badge-info">Unknown</span>`;
    const s = String(status).toLowerCase();
    
    let badgeClass = "badge-info";
    if (s.includes("verified") || s.includes("credited") || s.includes("accepted") || s.includes("healthy") || s.includes("pass") || s.includes("grade a")) {
      badgeClass = "badge-success";
    } else if (s.includes("pending") || s.includes("processing") || s.includes("initiated") || s.includes("warning") || s.includes("moderate") || s.includes("submitted") || s.includes("faq")) {
      badgeClass = "badge-warning";
    } else if (s.includes("failed") || s.includes("critical") || s.includes("high") || s.includes("below standard") || s.includes("urgent")) {
      badgeClass = "badge-danger";
    } else if (s.includes("operational") || s.includes("open") || s.includes("confirmed")) {
      badgeClass = "badge-primary";
    }

    return `<span class="badge ${badgeClass}">${status}</span>`;
  },

  // Modal Open / Close
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add("active");
      document.body.style.overflow = "hidden";
    }
  },

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove("active");
      document.body.style.overflow = "";
    }
  },

  // User Initials
  getInitials(name) {
    if (!name) return "KM";
    const parts = name.trim().split(" ");
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[1][0]).toUpperCase();
  },

  // Render Skeleton / Loading state
  renderLoading(container, text = "Loading data from server...") {
    if (typeof container === "string") container = document.getElementById(container);
    if (!container) return;
    container.innerHTML = `
      <div style="text-align: center; padding: 2.5rem 1rem; color: var(--text-muted);">
        <div class="spinner spinner-primary" style="width: 28px; height: 28px; margin-bottom: 0.75rem;"></div>
        <p style="font-size: 0.9rem;">${text}</p>
      </div>
    `;
  },

  // Render Empty State
  renderEmpty(container, icon, title, text, actionHtml = "") {
    if (typeof container === "string") container = document.getElementById(container);
    if (!container) return;
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">${icon}</div>
        <div class="empty-state-title">${title}</div>
        <div class="empty-state-text">${text}</div>
        ${actionHtml}
      </div>
    `;
  },

  // Render Error State with retry button
  renderError(container, errorMessage, retryCallback) {
    if (typeof container === "string") container = document.getElementById(container);
    if (!container) return;
    const retryId = `retry-btn-${Math.random().toString(36).substr(2, 6)}`;
    container.innerHTML = `
      <div class="empty-state" style="color: var(--danger-600);">
        <div class="empty-state-icon" style="color: var(--danger-600);">⚠</div>
        <div class="empty-state-title" style="color: var(--danger-600);">Unable to Load Content</div>
        <div class="empty-state-text" style="color: var(--text-muted);">${errorMessage || 'Network or server error.'}</div>
        ${retryCallback ? `<button id="${retryId}" class="btn btn-secondary btn-sm" style="margin-top: 0.5rem;">↻ Try Again</button>` : ''}
      </div>
    `;
    if (retryCallback) {
      setTimeout(() => {
        const btn = document.getElementById(retryId);
        if (btn) btn.onclick = retryCallback;
      }, 50);
    }
  }
};
