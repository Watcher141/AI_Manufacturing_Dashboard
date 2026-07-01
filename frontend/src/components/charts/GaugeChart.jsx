import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './charts.css';

const GaugeChart = ({ 
  value = 100, 
  title, 
  height = 180 
}) => {
  const data = [
    { name: 'value', value: value },
    { name: 'remainder', value: 100 - value }
  ];

  const getGaugeColor = () => {
    if (value >= 85) return 'var(--color-accent-lime)';
    if (value >= 70) return '#f59e0b';
    return 'var(--color-accent-pink)';
  };

  return (
    <div className="chart-wrapper" style={{ height, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="80%"
            startAngle={180}
            endAngle={0}
            innerRadius={65}
            outerRadius={80}
            dataKey="value"
            stroke="none"
          >
            <Cell fill={getGaugeColor()} />
            <Cell fill="var(--color-on-dark-faint)" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div style={{ position: 'absolute', bottom: '20%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <span style={{ fontSize: '1.8rem', fontFamily: 'var(--font-display)', fontWeight: 700 }}>
          {value.toFixed(0)}%
        </span>
        {title && <span style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{title}</span>}
      </div>
    </div>
  );
};

export default GaugeChart;
  
