import React from 'react';
import useAppStore from '../../store/useAppStore';
import useDashboardStore from '../../store/useDashboardStore';
import { Bell, RefreshCw } from 'lucide-react';

const Topbar = () => {
  const { activePage } = useAppStore();
  const { overview, fetchOverview, loading } = useDashboardStore();

  const getPageTitle = () => {
    switch (activePage) {
      case 'dashboard': return 'Dashboard Overview';
      case 'maintenance': return 'Predictive Maintenance';
      case 'defects': return 'Defect Detection';
      case 'inventory': return 'Inventory & Forecasting';
      case 'equipment': return 'Equipment Catalog';
      case 'alerts': return 'Alert Center';
      case 'ai_assistant': return 'AI Manufacturing Assistant';
      case 'settings': return 'System Settings';
      default: return 'Manufacturing Dashboard';
    }
  };

  const handleRefresh = async () => {
    try {
      await fetchOverview();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <header className="topbar">
      <h1 className="topbar-title">{getPageTitle()}</h1>

      <div className="topbar-actions">
        {overview && (
          <div className="status-summary">
            <div className="status-pill">
              <div className="status-dot"></div>
              <span>{overview.operational_count} Healthy</span>
            </div>
            {overview.critical_alerts > 0 && (
              <div className="status-pill">
                <div className="status-dot critical"></div>
                <span>{overview.critical_alerts} Critical Alerts</span>
              </div>
            )}
          </div>
        )}

        <button 
          onClick={handleRefresh} 
          className="toggle-btn" 
          disabled={loading}
          title="Refresh Data"
          style={{ display: 'flex', gap: '6px', fontSize: '0.85rem' }}
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          {!loading ? 'Sync' : 'Syncing...'}
        </button>
      </div>
    </header>
  );
};

export default Topbar;
