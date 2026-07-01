import React, { useEffect, useState } from 'react';
import useDashboardStore from '../store/useDashboardStore';
import useAppStore from '../store/useAppStore';
import { getSensorTrends } from '../api/equipment';
import StatCard from '../components/ui/StatCard';
import Card from '../components/ui/Card';
import GaugeChart from '../components/charts/GaugeChart';
import LineChart from '../components/charts/LineChart';
import StatusIndicator from '../components/ui/StatusIndicator';
import Loader from '../components/ui/Loader';
import { formatDate } from '../utils/formatters';
import { 
  Activity, 
  Cpu, 
  AlertTriangle, 
  Boxes, 
  Zap, 
  TrendingUp, 
  ShieldAlert 
} from 'lucide-react';
import './Dashboard.css';

const Dashboard = () => {
  const { overview, loading, fetchOverview } = useDashboardStore();
  const { setActivePage } = useAppStore();
  const [sensorTrends, setSensorTrends] = useState([]);
  const [trendsLoading, setTrendsLoading] = useState(false);

  useEffect(() => {
    const fetchTrends = async () => {
      setTrendsLoading(true);
      try {
        const data = await getSensorTrends(null, 12); // Last 12h
        setSensorTrends(data);
      } catch (err) {
        console.error('Failed to fetch sensor trends:', err);
      } finally {
        setTrendsLoading(false);
      }
    };

    fetchTrends();
  }, [overview]);

  if (loading && !overview) {
    return <Loader type="shimmer" count={6} height="120px" />;
  }

  if (!overview) {
    return (
      <div style={{ textAlign: 'center', padding: '48px' }}>
        <h2>Unable to load dashboard data</h2>
        <p style={{ color: 'var(--color-on-dark-muted)', margin: '16px 0' }}>Please verify your backend connection.</p>
      </div>
    );
  }

  // Find color for heatmap health
  const getHealthColor = (score) => {
    if (score >= 85) return 'var(--color-accent-lime)';
    if (score >= 70) return '#f59e0b';
    return 'var(--color-accent-pink)';
  };

  return (
    <div className="animate-fade-in" style={{ position: 'relative' }}>
      <div className="starfield-bg"></div>

      {/* Sentry Display Header with Lime Keyword Chip */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700, lineHeight: 1.2 }}>
          Plant Operational <span style={{ 
            backgroundColor: 'var(--color-accent-lime)', 
            color: 'var(--color-ink-deep)', 
            borderRadius: 'var(--rounded-xs)', 
            padding: '2px 12px',
            fontSize: '2.3rem'
          }}>Efficiency</span> Status
        </h2>
        <p style={{ color: 'var(--color-on-dark-muted)', marginTop: '8px' }}>
          Real-time anomaly monitoring, automated defect scans, and stock demand forecasts.
        </p>
      </div>

      {/* KPI Cards Row */}
      <div className="stat-card-grid">
        <StatCard 
          title="Overall Equipment Health" 
          value={`${overview.avg_health_score}%`} 
          icon={Activity}
          desc="Mean health score across active machines"
        />
        <StatCard 
          title="OEE Percentage" 
          value={`${overview.oee_percentage}%`} 
          icon={Zap}
          desc="Overall Equipment Effectiveness index"
        />
        <StatCard 
          title="Defects Detected" 
          value={overview.total_defects_today} 
          icon={ShieldAlert}
          desc="New anomalies registered today"
          trend={overview.total_defects_week > 0 ? `${overview.total_defects_week} this week` : null}
        />
        <StatCard 
          title="Low Stock Items" 
          value={overview.inventory_low_stock} 
          icon={Boxes}
          desc="Parts/consumables below reorder threshold"
        />
      </div>

      {/* Main Charts & Analytics Grid */}
      <div className="dashboard-grid">
        {/* Real-time Sensor Trends LineChart */}
        <Card>
          <h3 className="dashboard-card-title">
            <TrendingUp size={18} style={{ color: 'var(--color-accent-lime)' }} />
            Sensor Trends (Temperature & Vibration)
          </h3>
          {trendsLoading ? (
            <Loader type="spinner" />
          ) : sensorTrends.length > 0 ? (
            <LineChart 
              data={sensorTrends[0]?.data || []} 
              dataKeys={['temperature', 'vibration']} 
            />
          ) : (
            <div style={{ padding: '48px', textAlign: 'center', color: 'var(--color-on-dark-muted)' }}>
              No sensor trends found
            </div>
          )}
        </Card>

        {/* OEE Gauge & Alert Panel */}
        <Card style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <h3 className="dashboard-card-title">
            <Zap size={18} style={{ color: 'var(--color-accent-lime)' }} />
            OEE Quality Split
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '32px', flexGrow: 1 }}>
            <GaugeChart value={overview.oee_percentage} title="Availability" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <StatusIndicator status="operational" label="Availability: 100% (High)" />
              <StatusIndicator status="warning" label="Performance: 85% (Calibrated)" />
              <StatusIndicator status="operational" label="Quality index: 99.4%" />
            </div>
          </div>
        </Card>

        {/* Heatmap Section */}
        <Card className="dashboard-full-width">
          <h3 className="dashboard-card-title">
            <Cpu size={18} style={{ color: 'var(--color-accent-lime)' }} />
            Equipment Health Index
          </h3>
          <div className="health-heatmap-grid">
            {overview.equipment_health_summary.map((eq) => (
              <div 
                key={eq.id} 
                className="heatmap-cell"
                onClick={() => setActivePage('equipment')}
              >
                <span className="heatmap-cell-name">{eq.name}</span>
                <span 
                  className="heatmap-cell-score" 
                  style={{ color: getHealthColor(eq.health_score) }}
                >
                  {eq.health_score.toFixed(0)}%
                </span>
                <span style={{ fontSize: '0.7rem', color: 'var(--color-on-dark-faint)', textTransform: 'uppercase', marginTop: '4px' }}>
                  {eq.status}
                </span>
              </div>
            ))}
          </div>
        </Card>

        {/* Recent Alerts Feed */}
        <Card className="dashboard-full-width">
          <h3 className="dashboard-card-title">
            <AlertTriangle size={18} style={{ color: 'var(--color-accent-pink)' }} />
            Active Systems Feed
          </h3>
          <div className="recent-alert-list">
            {overview.recent_alerts.map((alert) => (
              <div key={alert.id} className="recent-alert-item">
                <div 
                  className="recent-alert-dot" 
                  style={{ 
                    backgroundColor: alert.severity === 'critical' ? 'var(--color-accent-pink)' : 
                                     alert.severity === 'warning' ? '#f59e0b' : 
                                     'var(--color-accent-lime)'
                  }}
                ></div>
                <div style={{ fontWeight: 600 }}>{alert.title}</div>
                <div style={{ color: 'var(--color-on-dark-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '500px' }}>
                  {alert.message}
                </div>
                <span className="recent-alert-time">{formatDate(alert.created_at)}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
