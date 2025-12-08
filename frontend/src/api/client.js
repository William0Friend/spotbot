import axios from 'axios';

/**
 * API Client for SpotBot Backend
 * 
 * Centralized HTTP client using Axios with automatic auth token injection.
 * 
 * Architecture:
 * - All API calls go through this client (consistency)
 * - Auto-adds JWT token from localStorage to requests
 * - Handles base URL configuration (dev vs production)
 * 
 * Configuration:
 * - Dev: VITE_API_URL env var or localhost:8000
 * - Production: Set VITE_API_URL in build process
 * 
 * Why Axios over fetch:
 * - Interceptors for automatic token injection
 * - Better error handling
 * - Request/response transformation
 * - Built-in timeout support
 * 
 * @module api/client
 */

// Base URL from environment or default to local dev server
// Vite exposes env vars prefixed with VITE_
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,  // All API routes under /api/v1
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// REQUEST INTERCEPTOR - Auto-inject JWT Token
// ============================================================================
// Why: Every authenticated request needs Authorization header
apiClient.interceptors.request.use(
  (config) => {
    // Get JWT token from localStorage (set during login)
    const token = localStorage.getItem('token');
    if (token) {
      // Add Bearer token to Authorization header
      // Format: "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ============================================================================
// API METHODS - Organized by Feature
// ============================================================================

/**
 * Authentication API calls
 * 
 * @namespace auth
 */
export const auth = {
  /**
   * Register a new user account
   * @param {Object} data - {email, username, password}
   * @returns {Promise<UserResponse>} Created user data
   */
  register: (data) => apiClient.post('/auth/register', data),
  
  /**
   * Login with email + password, returns JWT token
   * @param {Object} data - {email, password}
   * @returns {Promise<{access_token: string, token_type: string}>}
   */
  login: (data) => apiClient.post('/auth/login', data),
  
  /**
   * Get current authenticated user profile
   * Requires valid JWT token in localStorage
   * @returns {Promise<UserResponse>} User profile data
   */
  getCurrentUser: () => apiClient.get('/auth/me'),
};

/**
 * AI Detection API calls
 * 
 * @namespace detection
 */
export const detection = {
  analyze: (data) => apiClient.post('/detect/', data),
  test: () => apiClient.get('/detect/test'),
};

// Submissions
export const submissions = {
  getAll: (skip = 0, limit = 100) => apiClient.get(`/submissions/?skip=${skip}&limit=${limit}`),
  getById: (id) => apiClient.get(`/submissions/${id}`),
};

export default apiClient;
