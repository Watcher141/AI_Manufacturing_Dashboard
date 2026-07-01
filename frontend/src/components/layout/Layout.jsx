import React, { useEffect } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import useAppStore from '../../store/useAppStore';
import useDashboardStore from '../../store/useDashboardStore';
import './Layout.css';

const Layout = ({ children }) => {
  const { sidebarCollapsed, setUnreadAlertCount } = useAppStore();
  const { fetchOverview, overview } = useDashboardStore();

  useEffect(() => {
    // Initial fetch
    fetchOverview().catch(console.error);

    // Refresh every 30 seconds
    const interval = setInterval(() => {
      fetchOverview().catch(console.error);
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (overview) {
      setUnreadAlertCount(overview.unread_alerts);
    }
  }, [overview]);

  return (
    <div className="layout-container">
      <Sidebar />
      <div className={`main-content ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <Topbar />
        <main className="page-body">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
