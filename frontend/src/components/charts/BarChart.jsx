import React from 'react';
import { ResponsiveContainer, BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { CHART_COLORS } from '../../utils/constants';
import './charts.css';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="chart-tooltip">
        <p className="chart-tooltip-label">{label}</p>
        {payload.map((p, idx) => (
          <div key={idx} className="chart-tooltip-item">
            <span style={{ color: p.color }}>{p.name}:</span>
            <span style={{ fontWeight: 600 }}>{p.value}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

const BarChart = ({ data = [], dataKey = "value", nameKey = "name", labelName = "Count", height = 300 }) => {
  return (
    <div className="chart-wrapper" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsBarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-hairline-violet)" />
          <XAxis 
            dataKey={nameKey} 
            stroke="var(--color-on-dark-muted)"
            fontSize={11}
          />
          <YAxis stroke="var(--color-on-dark-muted)" fontSize={11} />
          <Tooltip content={<CustomTooltip />} />
          <Bar 
            dataKey={dataKey} 
            name={labelName}
            fill={CHART_COLORS.violet} 
            radius={[4, 4, 0, 0]}
          />
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default BarChart;
