import React from 'react';
import { ResponsiveContainer, AreaChart as RechartsAreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { CHART_COLORS } from '../../utils/constants';
import './charts.css';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="chart-tooltip">
        <p className="chart-tooltip-label">{new Date(label).toLocaleDateString([], { month: 'short', day: 'numeric' })}</p>
        {payload.map((p, idx) => (
          <div key={idx} className="chart-tooltip-item">
            <span style={{ color: p.color }}>{p.name}:</span>
            <span style={{ fontWeight: 600 }}>{typeof p.value === 'number' ? p.value.toFixed(1) : p.value}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

const AreaChart = ({ data = [], height = 300 }) => {
  return (
    <div className="chart-wrapper" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsAreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-hairline-violet)" />
          <XAxis 
            dataKey="date" 
            tickFormatter={(str) => {
              try {
                return new Date(str).toLocaleDateString([], { month: 'short', day: 'numeric' });
              } catch (e) {
                return '';
              }
            }}
            stroke="var(--color-on-dark-muted)"
            fontSize={11}
          />
          <YAxis stroke="var(--color-on-dark-muted)" fontSize={11} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 11, paddingTop: 10 }} />
          
          {/* Shaded confidence interval band */}
          <Area 
            type="monotone" 
            dataKey="confidence_upper" 
            stroke="transparent" 
            fill="var(--color-accent-violet-mid)" 
            fillOpacity={0.15} 
            name="Upper Range"
          />
          <Area 
            type="monotone" 
            dataKey="confidence_lower" 
            stroke="transparent" 
            fill="var(--color-accent-violet-mid)" 
            fillOpacity={0.15} 
            name="Lower Range"
          />
          
          {/* Predicted Demand */}
          <Area 
            type="monotone" 
            dataKey="predicted_demand" 
            name="Predicted Demand" 
            stroke={CHART_COLORS.lime} 
            fill="rgba(194, 239, 78, 0.05)" 
            strokeWidth={2}
          />
        </RechartsAreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AreaChart;
