import { create } from 'zustand';

const useAppStore = create((set) => ({
  sidebarCollapsed: false,
  activePage: 'dashboard',
  unreadAlertCount: 0,
  globalLoading: false,
  
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
  setActivePage: (page) => set({ activePage: page }),
  setUnreadAlertCount: (count) => set({ unreadAlertCount: count }),
  setGlobalLoading: (loading) => set({ globalLoading: loading }),
}));

export default useAppStore;
