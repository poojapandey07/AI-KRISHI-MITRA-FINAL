/**
 * Authentication Management for AI Krishi Mitra
 */

class AuthService {
  constructor() {
    this.tokenKey = "krishi_token";
    this.farmerKey = "krishi_farmer";
  }

  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  getFarmer() {
    try {
      const data = localStorage.getItem(this.farmerKey);
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  }

  isAuthenticated() {
    return !!this.getToken();
  }

  setSession(token, farmer) {
    localStorage.setItem(this.tokenKey, token);
    localStorage.setItem(this.farmerKey, JSON.stringify(farmer));
    window.dispatchEvent(new CustomEvent("auth:change", { detail: { isAuthenticated: true, farmer } }));
  }

  clearSession() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.farmerKey);
    window.dispatchEvent(new CustomEvent("auth:change", { detail: { isAuthenticated: false, farmer: null } }));
  }

  async login(mobileOrEmail, password) {
    const res = await window.api.post("/api/auth/login", {
      mobileOrEmail: mobileOrEmail.trim(),
      password: password.trim()
    });

    if (res.success && res.data) {
      const farmerData = {
        farmerId: res.data.farmerId,
        fullName: res.data.fullName,
        mobile: res.data.mobile
      };
      this.setSession(res.data.access_token, farmerData);
      return res.data;
    }
    throw new Error(res.message || "Login failed");
  }

  async register(registrationData) {
    const res = await window.api.post("/api/auth/register", registrationData);
    if (res.success && res.data) {
      const farmerData = {
        farmerId: res.data.farmerId,
        fullName: res.data.fullName,
        mobile: res.data.mobile
      };
      this.setSession(res.data.access_token, farmerData);
      return res.data;
    }
    throw new Error(res.message || "Registration failed");
  }

  logout() {
    this.clearSession();
    window.utils.showToast("Logged out successfully.", "info");
    if (window.appRouter) {
      window.appRouter.showAuthModal();
    }
  }
}

window.auth = new AuthService();
