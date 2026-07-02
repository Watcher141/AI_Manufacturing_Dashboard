import React, { useEffect, useState } from 'react';
import { getAlertsList, markAlertRead, markAllAlertsRead, dismissAlert, getAlertCounts } from '../api/alerts';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Loader from '../components/ui/Loader';
import { formatDate } from '../utils/formatters';
import { 
  AlertTriangle, 
  Check, 
  Trash2, 
  Bell, 
  Wrench, 
  ShieldAlert, 
  Package, 
  CheckCheck 
} from 'lucide-react';
import './Alerts.css';
import useAuthStore from '../store/useAuthStore';

const AlertsPage = () => {
  const { isAdmin } = useAuthStore();
  const [alerts, setAlerts] = useState([]);
  const [counts, setCounts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const fetchData = async () => {
    try {
      const filters = {};
      if (severityFilter) filters.severity = severityFilter;
      if (typeFilter) filters.type = typeFilter;

      const [list, countData] = await Promise.all([
        getAlertsList(filters),
        getAlertCounts()
      ]);
      setAlerts(list);
      setCounts(countData);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchData().finally(() => setLoading(false));
  }, [severityFilter, typeFilter]);

  const handleMarkRead = async (id) => {
    try {
      await markAlertRead(id);
      await fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllAlertsRead();
      await fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDismiss = async (id) => {
    try {
      await dismissAlert(id);
      await fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const getAlertIcon = (type) => {
    switch (type) {
      case 'maintenance': return <Wrench size={18} style={{ color: 'var(--color-accent-violet)' }} />;
      case 'defect': return <ShieldAlert size={18} style={{ color: 'var(--color-accent-pink)' }} />;
      case 'inventory': return <Package size={18} style={{ color: 'var(--color-accent-lime)' }} />;
      default: return <Bell size={18} />;
    }
  };

  if (loading && alerts.length === 0) {
    return <Loader type="shimmer" count={5} height="90px" />;
  }

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700 }}>
          Alert <span style={{ backgroundColor: 'var(--color-accent-pink)', color: 'var(--color-primary)', borderRadius: 'var(--rounded-xs)', padding: '2px 12px' }}>Center</span>
        </h2>
        <p style={{ color: 'var(--color-on-dark-muted)', marginTop: '8px' }}>
          Centralized monitoring feed for machine anomalies, production defects, and inventory stock warnings.
        </p>
      </div>

      {/* Bulk actions and filter header */}
      <div className="alerts-header-actions">
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <select 
            value={severityFilter} 
            onChange={(e) => setSeverityFilter(e.target.value)}
            style={{
              backgroundColor: 'var(--color-canvas-dark)',
              border: '1px solid var(--color-hairline-violet)',
              color: 'var(--color-on-primary)',
              padding: '6px 12px',
              borderRadius: 'var(--rounded-sm)',
              outline: 'none',
            }}
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>

          <select 
            value={typeFilter} 
            onChange={(e) => setTypeFilter(e.target.value)}
            style={{
              backgroundColor: 'var(--color-canvas-dark)',
              border: '1px solid var(--color-hairline-violet)',
              color: 'var(--color-on-primary)',
              padding: '6px 12px',
              borderRadius: 'var(--rounded-sm)',
              outline: 'none',
            }}
          >
            <option value="">All Types</option>
            <option value="maintenance">Maintenance</option>
            <option value="defect">Defect</option>
            <option value="inventory">Inventory</option>
          </select>
        </div>

        {isAdmin && counts && counts.unread > 0 && (
          <Button variant="ghost" onClick={handleMarkAllRead}>
            <CheckCheck size={16} /> Mark all read
          </Button>
        )}
      </div>

      {/* Feed list */}
      <div className="alerts-container">
        {alerts.length > 0 ? (
          alerts.map((alert) => (
            <div key={alert.id} className={`alert-feed-item ${!alert.is_read ? 'unread' : ''}`}>
              <div style={{ marginTop: '4px' }}>
                {getAlertIcon(alert.type)}
              </div>

              <div className="alert-feed-content">
                <div className="alert-feed-title" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  {alert.title}
                  <Badge status={alert.severity}>{alert.severity}</Badge>
                </div>
                <p className="alert-feed-desc">{alert.message}</p>
                <div className="alert-feed-meta">
                  <span>Category: {alert.type.toUpperCase()}</span>
                  {alert.equipment_name && <span>Equipment: {alert.equipment_name}</span>}
                  <span>Timestamp: {formatDate(alert.created_at)}</span>
                </div>
              </div>

              {isAdmin && (
                <div className="alert-feed-actions">
                  {!alert.is_read && (
                    <button 
                      onClick={() => handleMarkRead(alert.id)} 
                      className="toggle-btn"
                      title="Mark as read"
                      style={{ color: 'var(--color-accent-lime)' }}
                    >
                      <Check size={18} />
                    </button>
                  )}
                  <button 
                    onClick={() => handleDismiss(alert.id)} 
                    className="toggle-btn"
                    title="Dismiss alert"
                    style={{ color: 'var(--color-accent-pink)' }}
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              )}
            </div>
          ))
        ) : (
          <div style={{ textAlign: 'center', padding: '48px', backgroundColor: 'var(--color-surface-night)', border: '1px solid var(--color-hairline-violet)', borderRadius: 'var(--rounded-lg)' }}>
            <p style={{ color: 'var(--color-on-dark-muted)' }}>No alerts matching the active filters.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertsPage;
