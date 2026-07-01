import React from 'react';
import { ResponsiveContainer, LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { CHART_COLORS } from '../../utils/constants';
import './charts.css';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="chart-tooltip">
        <p className="chart-tooltip-label">{new Date(label).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
        {payload.map((p, idx) => (
          <div key={idx} className="chart-tooltip-item">
            <span style={{ color: p.color }}>{p.name}:</span>
            <span style={{ fontWeight: 600 }}>{p.value.toFixed(1)}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

const LineChart = ({ data = [], dataKeys = [], height = 300 }) => {
  const colors = [CHART_COLORS.lime, CHART_COLORS.pink, CHART_COLORS.violet, CHART_COLORS.onPrimary];

  return (
    <div className="chart-wrapper" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsLineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-hairline-violet)" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={(str) => {
              try {
                return new Date(str).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
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
          {dataKeys.map((key, idx) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              name={key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}
              stroke={colors[idx % colors.length]}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6 }}
            />
          ))}
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LineChart;
