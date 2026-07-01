import React, { useEffect, useState } from 'react';
import { getPredictions, getMaintenanceSchedule, getEquipmentPrediction, getMaintenanceLogs } from '../api/maintenance';
import { getSensorHistory } from '../api/equipment';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Loader from '../components/ui/Loader';
import Modal from '../components/ui/Modal';
import LineChart from '../components/charts/LineChart';
import GaugeChart from '../components/charts/GaugeChart';
import { formatDate } from '../utils/formatters';
import { Wrench, Calendar, AlertTriangle, ChevronRight, Activity } from 'lucide-react';
import './PredictiveMaintenance.css';

const PredictiveMaintenance = () => {
  const [predictions, setPredictions] = useState([]);
  const [schedule, setSchedule] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Detail Modal State
  const [selectedEquip, setSelectedEquip] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [sensorHistory, setSensorHistory] = useState([]);
  const [equipPrediction, setEquipPrediction] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [predData, schedData, logsData] = await Promise.all([
          getPredictions(),
          getMaintenanceSchedule(),
          getMaintenanceLogs()
        ]);
        setPredictions(predData);
        setSchedule(schedData);
        setLogs(logsData);
      } catch (err) {
        console.error('Failed to fetch maintenance details:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleOpenDetail = async (id) => {
    setSelectedEquip(id);
    setDetailLoading(true);
    try {
      const [pred, history] = await Promise.all([
        getEquipmentPrediction(id),
        getSensorHistory(id, 24)
      ]);
      setEquipPrediction(pred);
      setSensorHistory(history);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleCloseDetail = () => {
    setSelectedEquip(null);
    setEquipPrediction(null);
    setSensorHistory([]);
  };

  if (loading) {
    return <Loader type="shimmer" count={5} height="100px" />;
  }

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700 }}>
          Predictive <span style={{ backgroundColor: 'var(--color-accent-lime)', color: 'var(--color-ink-deep)', borderRadius: 'var(--rounded-xs)', padding: '2px 12px' }}>Maintenance</span>
        </h2>
        <p style={{ color: 'var(--color-on-dark-muted)', marginTop: '8px' }}>
          ML-driven remaining useful life estimates, anomaly scoring, and dynamic scheduling.
        </p>
      </div>

      <div className="maintenance-grid">
        {/* Predictions Feed */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <Card>
            <h3 className="dashboard-card-title" style={{ marginBottom: '24px' }}>
              <Activity size={18} style={{ color: 'var(--color-accent-lime)' }} />
              Equipment Failure Predictions
            </h3>

            <div className="predictions-list">
              {predictions.map((p) => (
                <div key={p.equipment_id} className="prediction-card">
                  <div className="prediction-info">
                    <span style={{ fontWeight: 700, fontSize: '1.05rem' }}>{p.name}</span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)' }}>{p.type} • {p.status.toUpperCase()}</span>
                    {p.predicted_failure_type !== 'none' && (
                      <span style={{ color: 'var(--color-accent-pink)', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
                        <AlertTriangle size={14} /> Risk: {p.predicted_failure_type.replace('_', ' ')}
                      </span>
                    )}
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
                    <div className="prediction-metric">
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-on-dark-muted)' }}>FAILURE RISK</span>
                      <span 
                        className="prediction-probability" 
                        style={{ color: p.failure_probability > 0.6 ? 'var(--color-accent-pink)' : p.failure_probability > 0.3 ? '#f59e0b' : 'var(--color-accent-lime)' }}
                      >
                        {(p.failure_probability * 100).toFixed(0)}%
                      </span>
                    </div>

                    <div className="prediction-metric" style={{ width: '100px' }}>
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-on-dark-muted)' }}>HEALTH</span>
                      <span style={{ fontFamily: 'var(--font-display)', fontSize: '1.25rem', fontWeight: 700 }}>
                        {p.health_score}%
                      </span>
                    </div>

                    <Button variant="ghost" onClick={() => handleOpenDetail(p.equipment_id)}>
                      Inspect <ChevronRight size={16} />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Maintenance Schedule */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <Card>
            <h3 className="dashboard-card-title">
              <Calendar size={18} style={{ color: 'var(--color-accent-lime)' }} />
              Dynamic Schedule
            </h3>
            <div className="schedule-list">
              {schedule.length > 0 ? (
                schedule.map((item, idx) => (
                  <div key={idx} className={`schedule-item ${item.urgency}`}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{item.name}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-on-dark-muted)' }}>{formatDate(item.recommended_date)}</div>
                    </div>
                    <Badge status={item.urgency}>{item.urgency}</Badge>
                  </div>
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: '24px', color: 'var(--color-on-dark-muted)' }}>
                  All systems healthy. No maintenance scheduled.
                </div>
              )}
            </div>
          </Card>

          {/* Maintenance Logs */}
          <Card>
            <h3 className="dashboard-card-title">
              <Wrench size={18} style={{ color: 'var(--color-accent-violet)' }} />
              Recent Logs
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {logs.slice(0, 5).map((log) => (
                <div key={log.id} style={{ borderBottom: '1px solid var(--color-hairline-violet)', paddingBottom: '10px', fontSize: '0.85rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                    <span>{log.maintenance_type.toUpperCase()}</span>
                    <span style={{ color: 'var(--color-accent-lime)' }}>${log.cost}</span>
                  </div>
                  <div style={{ color: 'var(--color-on-dark-muted)', margin: '4px 0' }}>{log.description}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-on-dark-faint)' }}>{formatDate(log.performed_at)} by {log.technician}</div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {/* Detail inspect modal */}
      <Modal isOpen={selectedEquip !== null} onClose={handleCloseDetail} title="Equipment Inspection Details">
        {detailLoading ? (
          <Loader type="spinner" />
        ) : equipPrediction ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3>{equipPrediction.name}</h3>
                <p style={{ color: 'var(--color-on-dark-muted)' }}>{equipPrediction.type}</p>
              </div>
              <GaugeChart value={equipPrediction.health_score} title="Health score" height={130} />
            </div>

            <Card style={{ backgroundColor: 'var(--color-ink-deep)' }}>
              <h4 style={{ marginBottom: '10px', textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '0.5px' }}>ML Diagnostics</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.9rem' }}>
                <div>Anomaly Score: <strong>{(equipPrediction.anomaly.anomaly_score * 100).toFixed(0)}%</strong></div>
                <div>Anomaly detected: <strong>{equipPrediction.anomaly.is_anomaly ? 'YES' : 'NO'}</strong></div>
                <div>Failure probability: <strong>{(equipPrediction.failure.failure_probability * 100).toFixed(0)}%</strong></div>
                <div>Failure type: <strong>{equipPrediction.failure.predicted_type}</strong></div>
              </div>
            </Card>

            <h4 style={{ textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '0.5px' }}>24h Sensor History</h4>
            <LineChart data={sensorHistory} dataKeys={['temperature', 'vibration', 'pressure']} height={200} />
          </div>
        ) : (
          <div>Failed to fetch detailed sensor stats.</div>
        )}
      </Modal>
    </div>
  );
};

export default PredictiveMaintenance;
