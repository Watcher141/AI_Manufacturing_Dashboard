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
  Factory,
  ShieldCheck,
  LogOut
} from 'lucide-react';
import useAppStore from '../../store/useAppStore';
import useAuthStore from '../../store/useAuthStore';

const Sidebar = () => {
  const { 
    sidebarCollapsed, 
    toggleSidebar, 
    activePage, 
    setActivePage, 
    unreadAlertCount 
  } = useAppStore();

  const { isAdmin, logout } = useAuthStore();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'maintenance', label: 'Predictive Maintenance', icon: Wrench },
    { id: 'defects', label: 'Defect Detection', icon: ShieldAlert },
    { id: 'inventory', label: 'Inventory Forecast', icon: Package },
    { id: 'equipment', label: 'Equipment', icon: Cpu },
    { id: 'alerts', label: 'Alerts', icon: Bell, count: unreadAlertCount },
    { id: 'ai_assistant', label: 'AI Assistant', icon: Bot },
  ];

  // Only show Settings for admins
  if (isAdmin) {
    navItems.push({ id: 'settings', label: 'Settings', icon: Settings });
  }

  const handleAdminClick = async () => {
    if (isAdmin) {
      await logout();
      setActivePage('dashboard');
    } else {
      setActivePage('admin_login');
    }
  };

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

      {/* Admin login/logout at bottom */}
      <div style={{ 
        padding: 'var(--space-sm)', 
        borderTop: '1px solid var(--color-hairline-violet)',
        marginTop: 'auto' 
      }}>
        <div
          className={`nav-item ${activePage === 'admin_login' ? 'active' : ''}`}
          onClick={handleAdminClick}
          style={isAdmin ? { color: 'var(--color-accent-lime)' } : {}}
        >
          {isAdmin ? <LogOut size={20} /> : <ShieldCheck size={20} />}
          <span className="nav-label">
            {isAdmin ? 'Logout Admin' : 'Admin Login'}
          </span>
          {isAdmin && !sidebarCollapsed && (
            <span style={{
              marginLeft: 'auto',
              fontSize: '0.65rem',
              fontWeight: 700,
              padding: '2px 6px',
              borderRadius: 'var(--rounded-full)',
              background: 'rgba(194, 239, 78, 0.15)',
              color: 'var(--color-accent-lime)',
              border: '1px solid rgba(194, 239, 78, 0.3)',
              letterSpacing: '0.05em',
            }}>
              ADMIN
            </span>
          )}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
