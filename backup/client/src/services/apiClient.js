/**
 * API Client service with automatic token refresh
 */

const axios = require('axios');
const config = require('../config');

class ApiClient {
  constructor() {
    this.authClient = this.createAuthClient();
    this.apiClient = this.createApiClient();
    this.accessToken = null;
    this.refreshPromise = null;
  }

  /**
   * Create axios client for authentication server
   */
  createAuthClient() {
    const client = axios.create({
      baseURL: config.services.authServer,
      timeout: 10000,
      withCredentials: true,
      headers: { 'Content-Type': 'application/json' }
    });

    client.interceptors.request.use(
      (config) => {
        console.log(`[AUTH] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => Promise.reject(error)
    );

    return client;
  }

  /**
   * Create axios client for backend API with automatic token refresh
   */
  createApiClient() {
    const client = axios.create({
      baseURL: config.services.backendApi,
      timeout: 10000,
      headers: { 'Content-Type': 'application/json' }
    });

    // Add access token to requests
    client.interceptors.request.use((config) => {
      if (this.accessToken) {
        config.headers.Authorization = `Bearer ${this.accessToken}`;
      }
      return config;
    });

    // Handle token refresh on 401
    client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            if (!this.refreshPromise) {
              this.refreshPromise = this.refreshAccessToken();
            }
            
            await this.refreshPromise;
            this.refreshPromise = null;

            if (this.accessToken) {
              originalRequest.headers.Authorization = `Bearer ${this.accessToken}`;
              return client(originalRequest);
            }
          } catch (refreshError) {
            this.clearTokens();
            throw new Error('Authentication failed. Please log in again.');
          }
        }
        
        return Promise.reject(error);
      }
    );

    return client;
  }

  /**
   * Login user and store access token
   */
  async login(username, password) {
    try {
      const response = await this.authClient.post('/auth/login', { username, password });
      const { access_token, user } = response.data;
      this.accessToken = access_token;
      return { user, accessToken: access_token };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  /**
   * Refresh access token using refresh token cookie
   */
  async refreshAccessToken() {
    try {
      const response = await this.authClient.post('/auth/refresh');
      this.accessToken = response.data.access_token;
      return this.accessToken;
    } catch (error) {
      this.clearTokens();
      throw error;
    }
  }

  /**
   * Logout user and clear tokens
   */
  async logout() {
    try {
      await this.authClient.post('/auth/logout');
      this.clearTokens();
    } catch (error) {
      this.clearTokens();
      throw error;
    }
  }

  /**
   * Clear stored tokens
   */
  clearTokens() {
    this.accessToken = null;
    this.refreshPromise = null;
  }

  /**
   * Check if user is authenticated (has access token)
   */
  isAuthenticated() {
    return !!this.accessToken;
  }

  /**
   * Get protected data from backend API
   */
  async getProtectedData() {
    const response = await this.apiClient.get('/api/protected-data');
    return response.data;
  }

  /**
   * Get user profile from backend API
   */
  async getUserProfile() {
    const response = await this.apiClient.get('/api/user-profile');
    return response.data;
  }

  /**
   * Get admin-only data (requires admin group)
   */
  async getAdminData() {
    const response = await this.apiClient.get('/api/admin-only');
    return response.data;
  }

  /**
   * Get IT department data (requires IT department)
   */
  async getItDepartmentData() {
    try {
      const response = await this.apiClient.get('/api/it-department');
      return response.data;
    } catch (error) {
      console.error('[API] Failed to get IT department data:', error.message);
      throw error;
    }
  }

  /**
   * Perform a secure action
   */
  async performSecureAction(actionData) {
    try {
      const response = await this.apiClient.post('/api/secure-action', actionData);
      return response.data;
    } catch (error) {
      console.error('[API] Failed to perform secure action:', error.message);
      throw error;
    }
  }

  /**
   * Check health of backend services
   */
  async checkHealth() {
    try {
      const [authHealth, apiHealth] = await Promise.allSettled([
        this.authClient.get('/health'),
        this.apiClient.get('/health')
      ]);

      return {
        authServer: {
          status: authHealth.status === 'fulfilled' ? 'healthy' : 'unhealthy',
          data: authHealth.status === 'fulfilled' ? authHealth.value.data : null,
          error: authHealth.status === 'rejected' ? authHealth.reason.message : null
        },
        backendApi: {
          status: apiHealth.status === 'fulfilled' ? 'healthy' : 'unhealthy',
          data: apiHealth.status === 'fulfilled' ? apiHealth.value.data : null,
          error: apiHealth.status === 'rejected' ? apiHealth.reason.message : null
        }
      };
    } catch (error) {
      console.error('[API] Health check failed:', error.message);
      throw error;
    }
  }
}

// Export singleton instance
module.exports = new ApiClient(); 