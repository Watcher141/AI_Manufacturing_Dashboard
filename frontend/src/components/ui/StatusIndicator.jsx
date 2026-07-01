import React from 'react';
import './ui.css';

const StatusIndicator = ({ 
  status = 'operational', 
  label 
}) => {
  const getDotClass = () => {
    switch (status.toLowerCase()) {
      case 'operational': return 'status-dot';
      case 'warning': return 'status-dot warning';
      case 'critical': return 'status-dot critical';
      case 'offline': return 'status-dot offline';
      default: return 'status-dot';
    }
  };

  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem' }}>
      <div className={getDotClass()}></div>
      {label && <span style={{ color: 'var(--color-on-dark-muted)' }}>{label}</span>}
    </div>
  );
};

export default StatusIndicator;
