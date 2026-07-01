import { create } from 'zustand';
import { getDashboardOverview } from '../api/dashboard';
import { getAlertCounts } from '../api/alerts';

const useDashboardStore = create((set, get) => ({
  overview: null,
  loading: false,
  error: null,
  lastUpdated: null,

  fetchOverview: async () => {
    set({ loading: true, error: null });
    try {
      const data = await getDashboardOverview();
      const alertCounts = await getAlertCounts();
      set({
        overview: data,
        loading: false,
        lastUpdated: new Date().toISOString(),
      });
      return data;
    } catch (err) {
      set({ error: err.message || 'Failed to fetch overview', loading: false });
      throw err;
    }
  },
}));

export default useDashboardStore;
