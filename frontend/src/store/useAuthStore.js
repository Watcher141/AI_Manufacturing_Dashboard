import { create } from 'zustand';
import { login as apiLogin, verify as apiVerify, logout as apiLogout } from '../api/auth';

const TOKEN_KEY = 'sentry_fab_admin_token';

const useAuthStore = create((set, get) => ({
  isAdmin: false,
  token: localStorage.getItem(TOKEN_KEY) || null,
  loading: false,
  error: null,

  /**
   * Log in with admin password.
   */
  login: async (password) => {
    set({ loading: true, error: null });
    try {
      const data = await apiLogin(password);
      localStorage.setItem(TOKEN_KEY, data.token);
      set({ isAdmin: true, token: data.token, loading: false });
      return data;
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed';
      set({ loading: false, error: message });
      throw new Error(message);
    }
  },

  /**
   * Verify saved token on app load.
   */
  checkAuth: async () => {
    const token = get().token;
    if (!token) {
      set({ isAdmin: false });
      return;
    }
    try {
      await apiVerify();
      set({ isAdmin: true });
    } catch {
      // Token is invalid or expired
      localStorage.removeItem(TOKEN_KEY);
      set({ isAdmin: false, token: null });
    }
  },

  /**
   * Log out and clear admin session.
   */
  logout: async () => {
    try {
      await apiLogout();
    } catch {
      // Even if server call fails, clear local state
    }
    localStorage.removeItem(TOKEN_KEY);
    set({ isAdmin: false, token: null, error: null });
  },

  clearError: () => set({ error: null }),
}));

export default useAuthStore;
