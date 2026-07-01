import React from 'react';
import Card from './Card';
import './ui.css';

const StatCard = ({ 
  title, 
  value, 
  icon: Icon, 
  desc, 
  trend, 
  trendDirection = 'up',
  style = {} 
}) => {
  const getTrendColor = () => {
    if (trendDirection === 'down') return 'var(--color-accent-pink)';
    return 'var(--color-accent-lime)';
  };

  return (
    <Card className="stat-card" style={style}>
      <div className="stat-card-title">{title}</div>
      <div className="stat-card-value">
        {value}
        {trend && (
          <span style={{ fontSize: '0.9rem', color: getTrendColor(), fontWeight: 600 }}>
            {trendDirection === 'up' ? '▲' : '▼'} {trend}
          </span>
        )}
      </div>
      {desc && <div className="stat-card-desc">{desc}</div>}
      {Icon && <Icon className="stat-card-icon" size={24} />}
    </Card>
  );
};

export default StatCard;
