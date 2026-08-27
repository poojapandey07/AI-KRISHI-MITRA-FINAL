/**
 * Reusable Centralized API Layer for AI Krishi Mitra
 * Handles authentication headers, error dispatching, and multipart uploads.
 */

// Dynamically use current host and protocol for local and network access
const API_BASE_URL = window.location.port === "8000" 
  ? window.location.origin 
  : `${window.location.protocol}//${window.location.hostname || '127.0.0.1'}:8000`;

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  getToken() {
    return localStorage.getItem("krishi_token");
  }

  getHeaders(isMultipart = false) {
    const headers = {};
    if (!isMultipart) {
      headers["Content-Type"] = "application/json";
    }
    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
    const isMultipart = options.body instanceof FormData;
    
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(isMultipart),
        ...(options.headers || {})
      }
    };

    try {
      const response = await fetch(url, config);
      const contentType = response.headers.get("content-type");
      let data = null;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        // Handle 401 Unauthorized (session expired)
        if (response.status === 401) {
          if (this.getToken()) {
            localStorage.removeItem("krishi_token");
            localStorage.removeItem("krishi_farmer");
            window.dispatchEvent(new CustomEvent("auth:expired"));
          }
        }
        
        const errorMsg = (data && data.detail) || (data && data.message) || `HTTP Error ${response.status}`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`[API Error] ${options.method || 'GET'} ${endpoint}:`, err.message);
      throw err;
    }
  }

  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "GET" });
  }

  post(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "POST",
      body: body instanceof FormData ? body : JSON.stringify(body)
    });
  }

  put(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(body)
    });
  }

  patch(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PATCH",
      body: JSON.stringify(body)
    });
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "DELETE" });
  }
}

// Global API singleton
window.api = new ApiService();
