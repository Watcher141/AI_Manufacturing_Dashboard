import React from 'react';
import { 
  LayoutDashboard, 
  Wrench, 
  ShieldAlert, 
  Package, 
  Settings, 
  Bot, 
  Bell, 
  Cpu, 
  ChevronLeft, 
  ChevronRight,
  Factory
} from 'lucide-react';
import useAppStore from '../../store/useAppStore';

const Sidebar = () => {
  const { 
    sidebarCollapsed, 
    toggleSidebar, 
    activePage, 
    setActivePage, 
    unreadAlertCount 
  } = useAppStore();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'maintenance', label: 'Predictive Maintenance', icon: Wrench },
    { id: 'defects', label: 'Defect Detection', icon: ShieldAlert },
    { id: 'inventory', label: 'Inventory Forecast', icon: Package },
    { id: 'equipment', label: 'Equipment', icon: Cpu },
    { id: 'alerts', label: 'Alerts', icon: Bell, count: unreadAlertCount },
    { id: 'ai_assistant', label: 'AI Assistant', icon: Bot },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="logo-container">
          <Factory size={24} className="text-lime" style={{ color: 'var(--color-accent-lime)' }} />
          {!sidebarCollapsed && <span className="logo-text">SENTRY FAB</span>}
        </div>
        <button onClick={toggleSidebar} className="toggle-btn" aria-label="Toggle Sidebar">
          {sidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.id}
              className={`nav-item ${activePage === item.id ? 'active' : ''}`}
              onClick={() => setActivePage(item.id)}
            >
              <Icon size={20} />
              <span className="nav-label">{item.label}</span>
              {item.count > 0 && !sidebarCollapsed && (
                <span className="badge-count">{item.count}</span>
              )}
            </div>
          );
        })}
      </nav>
    </aside>
  );
};

export default Sidebar;
