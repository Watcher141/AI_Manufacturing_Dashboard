import React from 'react';
import useAppStore from './store/useAppStore';
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

function App() {
  const { activePage } = useAppStore();

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
        return <SettingsPage />;
      default:
        return <Dashboard />;
    }
  };

  return <Layout>{renderPage()}</Layout>;
}

export default App;
