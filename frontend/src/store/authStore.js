/**
 * Authentication State Management with Zustand
 * 
 * Global state store for user authentication status using Zustand.
 * 
 * Why Zustand over Redux/Context:
 * - Simpler API: No providers, actions, reducers
 * - Less boilerplate: Define state + actions together
 * - Better performance: Component re-renders only when used state changes
 * - Smaller bundle: ~1KB vs Redux's ~8KB
 * 
 * State persistence:
 * - JWT token stored in localStorage (survives page refresh)
 * - On app load, token presence determines initial auth state
 * - User data fetched from API on first authenticated request
 * 
 * Security note:
 * - localStorage is vulnerable to XSS attacks
 * - Alternative: httpOnly cookies (requires backend changes)
 * - Tradeoff: localStorage easier for mobile apps, cookies better security
 * 
 * Usage in components:
 * ```jsx
 * const { isAuthenticated, user, logout } = useAuthStore()
 * if (isAuthenticated) { ... }
 * ```
 * 
 * @module store/authStore
 */

import { create } from 'zustand';

/**
 * Authentication store hook
 * 
 * @typedef {Object} AuthState
 * @property {Object|null} user - Current user profile (null if not logged in)
 * @property {string|null} token - JWT access token
 * @property {boolean} isAuthenticated - Quick check for auth status
 * @property {Function} setAuth - Store token and user after login
 * @property {Function} logout - Clear auth state and token
 */
const useAuthStore = create((set) => ({
  // Current user profile (null until fetched from API)
  user: null,
  
  // JWT token from localStorage (persists across page refreshes)
  token: localStorage.getItem('token'),
  
  // Quick boolean check: do we have a token?
  // Note: Token could be expired, but we'll handle that in API interceptor
  isAuthenticated: !!localStorage.getItem('token'),
  
  /**
   * Set authentication after successful login
   * 
   * Stores token in localStorage and updates state
   * 
   * @param {string} token - JWT access token from backend
   * @param {Object} user - User profile data
   */
  setAuth: (token, user) => {
    localStorage.setItem('token', token);
    set({ token, user, isAuthenticated: true });
  },
  
  /**
   * Logout user and clear authentication state
   * 
   * Removes token from localStorage and resets state
   * Component will re-render and redirect to login
   */
  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, user: null, isAuthenticated: false });
  },
}));

export default useAuthStore;
