import React, { useEffect, useState } from 'react';
import { getEquipmentList, getEquipmentDetail, getEquipmentTypes, getSensorHistory } from '../api/equipment';
import { getMaintenanceLogs } from '../api/maintenance';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Loader from '../components/ui/Loader';
import Modal from '../components/ui/Modal';
import LineChart from '../components/charts/LineChart';
import GaugeChart from '../components/charts/GaugeChart';
import { formatDate } from '../utils/formatters';
import { Cpu, MapPin, Wrench, Settings, ChevronRight, Activity } from 'lucide-react';
import './Equipment.css';

const EquipmentPage = () => {
  const [equipment, setEquipment] = useState([]);
  const [types, setTypes] = useState([]);
  const [selectedType, setSelectedType] = useState('');
  const [loading, setLoading] = useState(true);

  // Inspector Modal State
  const [inspectId, setInspectId] = useState(null);
  const [inspectDetail, setInspectDetail] = useState(null);
  const [sensorHistory, setSensorHistory] = useState([]);
  const [maintenanceHistory, setMaintenanceHistory] = useState([]);
  const [inspectLoading, setInspectLoading] = useState(false);

  useEffect(() => {
    const fetchTypes = async () => {
      try {
        const typesData = await getEquipmentTypes();
        setTypes(typesData);
      } catch (err) {
        console.error(err);
      }
    };
    fetchTypes();
  }, []);

  useEffect(() => {
    const fetchList = async () => {
      setLoading(true);
      try {
        const data = await getEquipmentList(selectedType ? { type: selectedType } : {});
        setEquipment(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchList();
  }, [selectedType]);

  const handleInspect = async (id) => {
    setInspectId(id);
    setInspectLoading(true);
    try {
      const [detail, sensors, maintenance] = await Promise.all([
        getEquipmentDetail(id),
        getSensorHistory(id, 24),
        getMaintenanceLogs(id)
      ]);
      setInspectDetail(detail);
      setSensorHistory(sensors);
      setMaintenanceHistory(maintenance);
    } catch (err) {
      console.error(err);
    } finally {
      setInspectLoading(false);
    }
  };

  const handleCloseInspect = () => {
    setInspectId(null);
    setInspectDetail(null);
    setSensorHistory([]);
    setMaintenanceHistory([]);
  };

  const getHealthColor = (score) => {
    if (score >= 85) return 'var(--color-accent-lime)';
    if (score >= 70) return '#f59e0b';
    return 'var(--color-accent-pink)';
  };

  if (loading && equipment.length === 0) {
    return <Loader type="shimmer" count={6} height="120px" />;
  }

  return (
    <div className="animate-fade-in">
      {/* Page Title */}
      <div style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700 }}>
            Equipment <span style={{ backgroundColor: 'var(--color-accent-lime)', color: 'var(--color-ink-deep)', borderRadius: 'var(--rounded-xs)', padding: '2px 12px' }}>Catalog</span>
          </h2>
          <p style={{ color: 'var(--color-on-dark-muted)', marginTop: '8px' }}>
            Browse inventory catalog details, locate machines, and inspect sensor metrics.
          </p>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--color-on-dark-muted)' }}>Filter type:</span>
          <select 
            value={selectedType} 
            onChange={(e) => setSelectedType(e.target.value)}
            style={{
              backgroundColor: 'var(--color-surface-night)',
              border: '1px solid var(--color-hairline-violet)',
              color: 'var(--color-on-primary)',
              padding: '8px 12px',
              borderRadius: 'var(--rounded-sm)',
              outline: 'none',
              fontFamily: 'var(--font-ui)',
            }}
          >
            <option value="">All Equipment</option>
            {types.map((type) => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Catalog Grid */}
      <div className="equipment-grid">
        {equipment.map((eq) => (
          <Card key={eq.id} className="equipment-card">
            <div className="equipment-card-header">
              <div>
                <h4 style={{ fontWeight: 700, fontSize: '1.1rem' }}>{eq.name}</h4>
                <p style={{ color: 'var(--color-on-dark-muted)', fontSize: '0.75rem' }}>{eq.manufacturer} {eq.model_number}</p>
              </div>
              <Badge status={eq.status}>{eq.status}</Badge>
            </div>

            <div className="equipment-card-body" style={{ marginTop: '12px', fontSize: '0.85rem', color: 'var(--color-on-dark-muted)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                <Cpu size={14} />
                <span>Type: {eq.type}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <MapPin size={14} />
                <span>Location: {eq.location}</span>
              </div>
            </div>

            <div className="equipment-card-footer">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-on-dark-muted)' }}>HEALTH:</span>
                <strong style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', color: getHealthColor(eq.health_score) }}>
                  {eq.health_score.toFixed(0)}%
                </strong>
              </div>

              <Button variant="ghost" onClick={() => handleInspect(eq.id)} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
                Inspect <ChevronRight size={14} />
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Detail inspect modal */}
      <Modal isOpen={inspectId !== null} onClose={handleCloseInspect} title="Detailed Equipment Inspector">
        {inspectLoading ? (
          <Loader type="spinner" />
        ) : inspectDetail ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3>{inspectDetail.name}</h3>
                <p style={{ color: 'var(--color-on-dark-muted)', fontSize: '0.85rem' }}>
                  {inspectDetail.manufacturer} {inspectDetail.model_number} • {inspectDetail.location}
                </p>
                <div style={{ marginTop: '8px', display: 'flex', gap: '8px' }}>
                  <Badge status={inspectDetail.status}>{inspectDetail.status}</Badge>
                  <span style={{ fontSize: '0.85rem', color: 'var(--color-on-dark-muted)' }}>
                    Installed: {new Date(inspectDetail.install_date).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <GaugeChart value={inspectDetail.health_score} title="Health score" height={130} />
            </div>

            {/* Sensor Line Chart */}
            <h4 style={{ textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '0.5px' }}>24h Sensor History</h4>
            <LineChart data={sensorHistory} dataKeys={['temperature', 'vibration', 'pressure', 'power_consumption']} height={200} />

            {/* Maintenance History list */}
            <h4 style={{ textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '0.5px' }}>Maintenance Log history</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '150px', overflowY: 'auto' }}>
              {maintenanceHistory.length > 0 ? (
                maintenanceHistory.map((log) => (
                  <div key={log.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', backgroundColor: 'var(--color-ink-deep)', border: '1px solid var(--color-hairline-violet)', borderRadius: 'var(--rounded-md)', fontSize: '0.85rem' }}>
                    <div>
                      <strong style={{ textTransform: 'capitalize' }}>{log.maintenance_type}</strong>
                      <div style={{ color: 'var(--color-on-dark-muted)' }}>{log.description}</div>
                    </div>
                    <div style={{ textDirection: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                      <span style={{ color: 'var(--color-accent-lime)' }}>${log.cost}</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-on-dark-faint)' }}>{new Date(log.performed_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: '12px', color: 'var(--color-on-dark-muted)', fontSize: '0.85rem' }}>
                  No maintenance records registered for this machine.
                </div>
              )}
            </div>
          </div>
        ) : (
          <div>Failed to retrieve diagnostic data.</div>
        )}
      </Modal>
    </div>
  );
};

export default EquipmentPage;
