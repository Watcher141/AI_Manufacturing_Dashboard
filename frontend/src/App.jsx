import React, { useEffect } from 'react';
import useAppStore from './store/useAppStore';
import useAuthStore from './store/useAuthStore';
import Layout from './components/layout/Layout';

// Pages
import Dashboard from './pages/Dashboard';
import PredictiveMaintenance from './pages/PredictiveMaintenance';
import DefectDetection from './pages/DefectDetection';
import InventoryForecasting from './pages/InventoryForecasting';
import EquipmentPage from './pages/Equipment';
import AlertsPage from './pages/Alerts';
import AIAssistant from './pages/AIAssistant';
import SettingsPage from './pages/Settings';
import AdminLogin from './pages/AdminLogin';

function App() {
  const { activePage, setActivePage } = useAppStore();
  const { isAdmin, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth().catch(console.error);
  }, [checkAuth]);

  // Admin access guard for settings page
  useEffect(() => {
    if (activePage === 'settings' && !isAdmin) {
      setActivePage('admin_login');
    }
  }, [activePage, isAdmin, setActivePage]);

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard />;
      case 'maintenance':
        return <PredictiveMaintenance />;
      case 'defects':
        return <DefectDetection />;
      case 'inventory':
        return <InventoryForecasting />;
      case 'equipment':
        return <EquipmentPage />;
      case 'alerts':
        return <AlertsPage />;
      case 'ai_assistant':
        return <AIAssistant />;
      case 'settings':
        return isAdmin ? <SettingsPage /> : <AdminLogin />;
      case 'admin_login':
        return <AdminLogin />;
      default:
        return <Dashboard />;
    }
  };

  return <Layout>{renderPage()}</Layout>;
}

export default App;
