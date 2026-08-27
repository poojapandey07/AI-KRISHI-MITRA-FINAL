/**
 * Module 3: Krishi Finance Controller
 */

window.FinanceModule = {
  initialized: false,
  currentBank: null,
  activeFilter: "all",

  init() {
    this.bindEvents();
    this.loadData();
    this.initialized = true;
  },

  bindEvents() {
    const formLinkBank = document.getElementById("form-link-bank");
    if (formLinkBank) {
      formLinkBank.onsubmit = (e) => this.handleLinkBank(e);
    }

    const filterGroup = document.getElementById("payment-filter-group");
    if (filterGroup) {
      filterGroup.addEventListener("click", (e) => {
        const btn = e.target.closest(".filter-pill");
        if (btn) {
          filterGroup.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
          btn.classList.add("active");
          this.activeFilter = btn.dataset.filter;
          this.loadPayments(this.activeFilter);
        }
      });
    }
  },

  async loadData() {
    try {
      await Promise.all([
        this.loadBankAccount(),
        this.loadPayments(this.activeFilter)
      ]);
    } catch (err) {
      console.error("Error loading finance data:", err);
    }
  },

  async loadBankAccount() {
    const container = document.getElementById("bank-account-content");
    const pill = document.getElementById("bank-verification-pill");
    if (!container) return;

    window.utils.renderLoading(container, "Checking bank link status...");

    try {
      const res = await window.api.get("/api/finance/bank");
      if (res.success && res.data) {
        this.currentBank = res.data;
        const b = res.data;

        if (pill) {
          pill.innerHTML = window.utils.getStatusBadge(b.verificationStatus);
        }

        container.innerHTML = `
          <div class="bank-card-visual">
            <div class="bank-card-top">
              <span class="bank-card-name">🏛️ ${b.bankName}</span>
              <span style="font-size: 0.75rem; background: rgba(255,255,255,0.2); padding: 0.2rem 0.5rem; border-radius: 4px;">
                ${b.bankAccountId}
              </span>
            </div>
            <div class="bank-card-number">${b.maskedAccountNumber}</div>
            <div class="bank-card-bottom">
              <div>
                <div style="font-size: 0.7rem; opacity: 0.8;">ACCOUNT HOLDER</div>
                <div class="bank-card-holder">${b.accountHolder}</div>
              </div>
              <div>
                <div style="font-size: 0.7rem; opacity: 0.8;">IFSC CODE</div>
                <div class="bank-card-ifsc">${b.ifscCode}</div>
              </div>
            </div>
          </div>

          <div class="bank-actions-row">
            <button class="btn btn-outline btn-sm" onclick="utils.openModal('modal-link-bank')">
              ✏️ Update Bank Details
            </button>
            ${b.verificationStatus !== "Verified" ? `
              <button class="btn btn-secondary btn-sm" onclick="FinanceModule.verifyBankSandbox('${b.bankAccountId}')">
                ⚡ Run NPCI Sandbox Verification
              </button>
            ` : `
              <span style="font-size: 0.82rem; color: var(--success-600); font-weight: 600;">
                ✓ Verified for Instant DBT Payouts
              </span>
            `}
          </div>
        `;
      } else {
        // No bank linked yet
        if (pill) pill.innerHTML = window.utils.getStatusBadge("Not Verified");
        container.innerHTML = `
          <div style="text-align: center; padding: 1.5rem; border: 2px dashed var(--border-light); border-radius: var(--radius-md);">
            <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🏦</div>
            <h4 style="color: var(--primary-900); margin-bottom: 0.25rem;">No Bank Account Linked</h4>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
              Link your bank account to receive direct procurement payments into your savings/kisan credit card account.
            </p>
            <button class="btn btn-primary btn-sm" onclick="utils.openModal('modal-link-bank')">
              + Link Bank Account
            </button>
          </div>
        `;
      }
    } catch (err) {
      window.utils.renderError(container, err.message, () => this.loadBankAccount());
    }
  },

  async loadPayments(filter = "all") {
    const tbody = document.getElementById("payments-tbody");
    const totalCreditedEl = document.getElementById("total-payout-credited");
    const totalProcessingEl = document.getElementById("total-payout-processing");
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem;">Loading payments...</td></tr>`;

    try {
      const endpoint = filter && filter !== "all" ? `/api/finance/payments?status=${encodeURIComponent(filter)}` : "/api/finance/payments";
      const res = await window.api.get(endpoint);
      if (res.success && res.data) {
        const payments = res.data;

        // Calculate Totals
        let creditedTotal = 0;
        let processingTotal = 0;

        // Fetch all payments for overall stats if filtered
        const allRes = filter === "all" ? res : await window.api.get("/api/finance/payments");
        if (allRes.success && allRes.data) {
          allRes.data.forEach(p => {
            if (p.status === "Payment Credited") creditedTotal += p.amount;
            else if (p.status === "Payment Processing" || p.status === "Payment Initiated") processingTotal += p.amount;
          });
        }

        if (totalCreditedEl) totalCreditedEl.textContent = window.utils.formatCurrency(creditedTotal);
        if (totalProcessingEl) totalProcessingEl.textContent = window.utils.formatCurrency(processingTotal);

        if (payments.length === 0) {
          tbody.innerHTML = `
            <tr>
              <td colspan="8" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
                No payment records matching the selected filter.
              </td>
            </tr>
          `;
          return;
        }

        tbody.innerHTML = payments.map(p => `
          <tr>
            <td><strong>${p.paymentId}</strong></td>
            <td><small style="color: var(--text-muted);">${p.procurementId}</small></td>
            <td><strong>${p.crop}</strong> (${p.quantityQuintals} Q)</td>
            <td>${p.bankName || 'Linked Bank'} <br><small style="color: var(--text-muted); font-family: monospace;">${p.maskedAccountNumber || '-'}</small></td>
            <td class="amount-highlight">${window.utils.formatCurrency(p.amount)}</td>
            <td>${window.utils.getStatusBadge(p.status)}</td>
            <td><small>${window.utils.formatDate(p.date || p.initiatedAt)}</small></td>
            <td>
              ${p.status === "Payment Initiated" ? `
                <button class="btn btn-secondary btn-sm" onclick="FinanceModule.advancePayment('${p.paymentId}', 'Payment Processing')">
                  Process →
                </button>
              ` : p.status === "Payment Processing" ? `
                <button class="btn btn-primary btn-sm" onclick="FinanceModule.advancePayment('${p.paymentId}', 'Payment Credited')">
                  Credit DBT →
                </button>
              ` : `
                <span style="font-size: 0.8rem; color: var(--success-600);">✓ Settled</span>
              `}
            </td>
          </tr>
        `).join("");
      }
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--danger-600); padding: 2rem;">Error: ${err.message}</td></tr>`;
    }
  },

  async handleLinkBank(e) {
    e.preventDefault();
    const bankName = document.getElementById("bank-name-input").value;
    const accountHolder = document.getElementById("bank-holder-input").value;
    const accountNumber = document.getElementById("bank-acc-input").value;
    const accConfirm = document.getElementById("bank-acc-confirm").value;
    const ifscCode = document.getElementById("bank-ifsc-input").value;

    if (accountNumber !== accConfirm) {
      window.utils.showToast("Account numbers do not match.", "warning");
      return;
    }

    try {
      const res = await window.api.post("/api/finance/bank", {
        bankName, accountHolder, accountNumber, ifscCode
      });

      if (res.success && res.data) {
        window.utils.showToast("Bank account linked! Verification pending.", "success");
        window.utils.closeModal("modal-link-bank");
        document.getElementById("form-link-bank").reset();
        await this.loadBankAccount();
      }
    } catch (err) {
      window.utils.showToast(err.message, "error");
    }
  },

  async verifyBankSandbox(bankAccountId) {
    try {
      const res = await window.api.post("/api/finance/bank/verify", {
        bankAccountId,
        action: "verify"
      });

      if (res.success && res.data) {
        window.utils.showToast("NPCI Sandbox Verification: Account verified successfully!", "success");
        await this.loadBankAccount();
      }
    } catch (err) {
      window.utils.showToast(err.message, "error");
    }
  },

  async advancePayment(paymentId, nextStatus) {
    try {
      const res = await window.api.patch(`/api/finance/payments/${paymentId}/simulate-status`, {
        status: nextStatus
      });

      if (res.success) {
        window.utils.showToast(`Payment transitioned to '${nextStatus}'.`, "success");
        await this.loadPayments(this.activeFilter);
      }
    } catch (err) {
      window.utils.showToast(err.message, "error");
    }
  }
};
