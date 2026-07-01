import React from 'react';
import { ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import { CHART_COLORS } from '../../utils/constants';
import './charts.css';

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="chart-tooltip">
        <p className="chart-tooltip-label">{payload[0].name}</p>
        <div className="chart-tooltip-item">
          <span>Value:</span>
          <span style={{ fontWeight: 600 }}>{payload[0].value}</span>
        </div>
      </div>
    );
  }
  return null;
};

const PieChart = ({ data = [], height = 300 }) => {
  const colors = [
    CHART_COLORS.lime,
    CHART_COLORS.pink,
    CHART_COLORS.violet,
    CHART_COLORS.purple,
    '#f59e0b',
    '#3b82f6',
  ];

  return (
    <div className="chart-wrapper" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 11, paddingTop: 10 }} />
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PieChart;
