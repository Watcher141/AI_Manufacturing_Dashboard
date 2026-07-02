import React, { useEffect, useState } from 'react';
import { getDefects, getDefectStats, triggerDefectScan, resolveDefect } from '../api/defects';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import DataTable from '../components/ui/DataTable';
import BarChart from '../components/charts/BarChart';
import PieChart from '../components/charts/PieChart';
import Loader from '../components/ui/Loader';
import { formatDate } from '../utils/formatters';
import { ShieldAlert, Play, CheckCircle, HelpCircle } from 'lucide-react';
import useAuthStore from '../store/useAuthStore';
import './DefectDetection.css';

const DefectDetection = () => {
  const { isAdmin } = useAuthStore();
  const [defects, setDefects] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);

  const fetchData = async () => {
    try {
      const [defectList, statsData] = await Promise.all([
        getDefects({ is_resolved: false }),
        getDefectStats()
      ]);
      setDefects(defectList);
      setStats(statsData);
    } catch (err) {
      console.error('Failed to fetch defect details:', err);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchData().finally(() => setLoading(false));
  }, []);

  const handleRunScan = async () => {
    setScanning(true);
    try {
      await triggerDefectScan();
      await fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setScanning(false);
    }
  };

  const handleResolve = async (id) => {
    try {
      await resolveDefect(id);
      await fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <Loader type="shimmer" count={5} height="90px" />;
  }

  // Formatting chart data
  const getBarChartData = () => {
    if (!stats || !stats.by_type) return [];
    return Object.entries(stats.by_type).map(([name, value]) => ({
      name: name.replace('_', ' ').toUpperCase(),
      value,
    }));
  };

  const getPieChartData = () => {
    if (!stats || !stats.by_equipment) return [];
    return Object.entries(stats.by_equipment).map(([name, value]) => ({
      name,
      value,
    }));
  };

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700 }}>
          Defect <span style={{ backgroundColor: 'var(--color-accent-lime)', color: 'var(--color-ink-deep)', borderRadius: 'var(--rounded-xs)', padding: '2px 12px' }}>Detection</span>
        </h2>
        <p style={{ color: 'var(--color-on-dark-muted)', marginTop: '8px' }}>
          Automated vision-based and sensor-derived defect classification and severity audits.
        </p>
      </div>

      {/* Manual scan trigger banner */}
      {isAdmin && (
        <div className="scan-action-banner">
          <div>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldAlert size={20} style={{ color: 'var(--color-accent-lime)' }} />
              Run Quality Scan Audit
            </h3>
            <p style={{ color: 'var(--color-on-dark-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
              Triggers ML defect classification models on all active production lines immediately.
            </p>
          </div>
          <Button onClick={handleRunScan} disabled={scanning}>
            <Play size={16} />
            {scanning ? 'Auditing lines...' : 'Run Audit'}
          </Button>
        </div>
      )}

      {/* Stats Summary Rows */}
      {stats && (
        <div className="defect-summary-row">
          <Card>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)' }}>UNRESOLVED FAULTS</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 700 }}>{stats.unresolved_count}</div>
          </Card>
          <Card>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)' }}>CRITICAL DEFECTS</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 700, color: 'var(--color-accent-pink)' }}>{stats.critical_count}</div>
          </Card>
          <Card>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)' }}>RESOLVED DEFECTS</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 700, color: 'var(--color-accent-lime)' }}>{stats.resolved_count}</div>
          </Card>
          <Card>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)' }}>RESOLUTION RATE</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 700 }}>{stats.resolution_rate}%</div>
          </Card>
        </div>
      )}

      {/* Charts Grid */}
      <div className="defect-dashboard-layout" style={{ marginBottom: '24px' }}>
        <Card>
          <h3 className="dashboard-card-title">Defect Type Distribution</h3>
          <BarChart data={getBarChartData()} />
        </Card>
        <Card>
          <h3 className="dashboard-card-title">Defects By Machine</h3>
          <PieChart data={getPieChartData()} />
        </Card>
      </div>

      {/* Unresolved Defects Table */}
      <Card>
        <h3 className="dashboard-card-title">Active Fault Register</h3>
        <DataTable
          headers={
            isAdmin 
              ? ['Equipment', 'Type', 'Severity', 'Confidence', 'Detected At', 'Actions']
              : ['Equipment', 'Type', 'Severity', 'Confidence', 'Detected At']
          }
          data={defects}
          renderRow={(d) => (
            <tr key={d.id}>
              <td style={{ fontWeight: 600 }}>{d.equipment_name}</td>
              <td style={{ textTransform: 'capitalize' }}>{d.defect_type.replace('_', ' ')}</td>
              <td>
                <Badge status={d.severity}>{d.severity}</Badge>
              </td>
              <td style={{ fontFamily: 'var(--font-code)' }}>{(d.confidence_score * 100).toFixed(1)}%</td>
              <td>{formatDate(d.timestamp)}</td>
              {isAdmin && (
                <td>
                  <Button variant="ghost" onClick={() => handleResolve(d.id)} style={{ padding: '6px 12px' }}>
                    <CheckCircle size={14} /> Resolve
                  </Button>
                </td>
              )}
            </tr>
          )}
        />
      </Card>
    </div>
  );
};

export default DefectDetection;
