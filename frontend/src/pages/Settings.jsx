import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { getAIStatus } from '../api/assistant';
import { Settings, Save, ShieldAlert, Key, Sliders, Database } from 'lucide-react';
import './Settings.css';

import useAuthStore from '../store/useAuthStore';

const SettingsPage = () => {
  const { isAdmin } = useAuthStore();
  const [apiKey, setApiKey] = useState('');
  const [tempThreshold, setTempThreshold] = useState(80);
  const [vibeThreshold, setVibeThreshold] = useState(4.0);
  const [refreshInterval, setRefreshInterval] = useState(30);
  const [aiStatus, setAiStatus] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!isAdmin) return;
    getAIStatus()
      .then(setAiStatus)
      .catch(console.error);
  }, [isAdmin]);

  if (!isAdmin) {
    return null; // Let layout or App component handle redirect
  }

  const handleSave = () => {
    setSaving(true);
    // Simulate save
    setTimeout(() => {
      setSaving(false);
      alert('System configurations saved successfully.');
    }, 800);
  };

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700 }}>
          System <span style={{ backgroundColor: 'var(--color-accent-lime)', color: 'var(--color-ink-deep)', borderRadius: 'var(--rounded-xs)', padding: '2px 12px' }}>Settings</span>
        </h2>
        <p style={{ color: 'var(--color-on-dark-muted)', marginTop: '8px' }}>
          Calibrate monitoring thresholds, modify polling intervals, and configure credentials.
        </p>
      </div>

      <div className="settings-grid">
        {/* ML Credentials Card */}
        <Card>
          <h3 className="dashboard-card-title">
            <Key size={18} style={{ color: 'var(--color-accent-lime)' }} />
            Groq API Credentials
          </h3>
          <div className="settings-group" style={{ marginTop: '16px' }}>
            <label className="form-label">GROQ API KEY</label>
            <input 
              type="password" 
              className="settings-input"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="••••••••••••••••••••••••••••••••••••••••"
            />
            {aiStatus && (
              <p style={{ fontSize: '0.8rem', color: aiStatus.available ? 'var(--color-accent-lime)' : 'var(--color-accent-pink)' }}>
                Status: {aiStatus.available ? `ONLINE (${aiStatus.model})` : 'OFFLINE (No key configured in backend environment)'}
              </p>
            )}
          </div>
        </Card>

        {/* Telemetry Thresholds Card */}
        <Card>
          <h3 className="dashboard-card-title">
            <ShieldAlert size={18} style={{ color: 'var(--color-accent-pink)' }} />
            Telemetry Anomaly Thresholds
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
            <div className="settings-row">
              <div>
                <strong style={{ display: 'block' }}>Vibration Threshold Limit</strong>
                <span style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)' }}>Flag warning status above target level</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input 
                  type="number" 
                  className="settings-input" 
                  value={vibeThreshold} 
                  onChange={(e) => setVibeThreshold(parseFloat(e.target.value))}
                  style={{ width: '80px' }}
                  step="0.1"
                />
                <span>mm/s</span>
              </div>
            </div>

            <div className="settings-row">
              <div>
                <strong style={{ display: 'block' }}>Temperature Limit</strong>
                <span style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)' }}>Alert temperature warnings beyond standard range</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input 
                  type="number" 
                  className="settings-input" 
                  value={tempThreshold} 
                  onChange={(e) => setTempThreshold(parseInt(e.target.value))}
                  style={{ width: '80px' }}
                />
                <span>°C</span>
              </div>
            </div>
          </div>
        </Card>

        {/* General Preferences Card */}
        <Card>
          <h3 className="dashboard-card-title">
            <Sliders size={18} style={{ color: 'var(--color-accent-violet)' }} />
            App Engine Polling Interval
          </h3>
          <div className="settings-row" style={{ marginTop: '16px' }}>
            <div>
              <strong style={{ display: 'block' }}>Background Dashboard Sync</strong>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)' }}>Rate of metrics updates and data synchronization cycles</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input 
                type="number" 
                className="settings-input" 
                value={refreshInterval} 
                onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
                style={{ width: '80px' }}
              />
              <span>Seconds</span>
            </div>
          </div>
        </Card>

        {/* Real Data Management Card */}
        <Card>
          <h3 className="dashboard-card-title">
            <Database size={18} style={{ color: 'var(--color-on-primary)' }} />
            Real Data Management
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
            <div className="settings-row" style={{ alignItems: 'flex-start' }}>
              <div>
                <strong style={{ display: 'block', color: 'var(--color-accent-pink)' }}>1. Clear Existing Data</strong>
                <span style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)' }}>Wipe synthetic telemetry to prepare for real data upload.</span>
              </div>
              <Button 
                variant="outline" 
                onClick={async () => {
                  if(window.confirm('Are you sure you want to delete all sensor data?')) {
                    try {
                      const { clearData } = await import('../api/settings');
                      const res = await clearData();
                      alert(res.message);
                    } catch (e) {
                      alert('Error clearing data: ' + e.message);
                    }
                  }
                }}
              >
                Clear Data
              </Button>
            </div>

            <div className="settings-row" style={{ alignItems: 'flex-start', borderTop: '1px solid var(--color-surface-hover)', paddingTop: '16px' }}>
              <div>
                <strong style={{ display: 'block', color: 'var(--color-accent-lime)' }}>2. Upload Real Data (CSV)</strong>
                <span style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)', display: 'block', marginBottom: '8px' }}>
                  Upload your factory sensor data. Required columns: <br/>
                  <code style={{ fontSize: '0.7rem', backgroundColor: 'var(--color-bg-deep)', padding: '2px 4px', borderRadius: '4px' }}>equipment_id, timestamp, temperature, vibration, pressure, power_consumption</code>
                </span>
                <input 
                  type="file" 
                  accept=".csv"
                  onChange={async (e) => {
                    const file = e.target.files[0];
                    if (file) {
                      try {
                        const { uploadData } = await import('../api/settings');
                        const res = await uploadData(file);
                        alert(res.message);
                      } catch (err) {
                        alert('Upload failed: ' + (err.response?.data?.detail || err.message));
                      }
                    }
                  }}
                  style={{ color: 'var(--color-on-dark-muted)' }}
                />
              </div>
            </div>

            <div className="settings-row" style={{ alignItems: 'flex-start', borderTop: '1px solid var(--color-surface-hover)', paddingTop: '16px' }}>
              <div>
                <strong style={{ display: 'block', color: 'var(--color-accent-violet)' }}>3. Retrain AI Models</strong>
                <span style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)' }}>Trigger the backend to learn from the newly uploaded data.</span>
              </div>
              <Button 
                onClick={async () => {
                  try {
                    const { retrainModels } = await import('../api/settings');
                    const res = await retrainModels();
                    alert(res.message);
                  } catch (e) {
                    alert('Error retraining models: ' + e.message);
                  }
                }}
              >
                Retrain AI
              </Button>
            </div>
          </div>
        </Card>

        {/* Action Row */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '12px' }}>
          <Button onClick={handleSave} disabled={saving} style={{ display: 'flex', gap: '8px' }}>
            <Save size={16} />
            {saving ? 'Saving System configurations...' : 'Save Configuration'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
