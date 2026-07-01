import React from 'react';
import './ui.css';

export const Spinner = () => {
  return <div className="spinner"></div>;
};

export const Skeleton = ({ 
  width = '100%', 
  height = '16px', 
  style = {} 
}) => {
  return (
    <div 
      className="shimmer" 
      style={{ 
        width, 
        height, 
        backgroundColor: 'var(--color-surface-night)', 
        ...style 
      }}
    ></div>
  );
};

const Loader = ({ 
  type = 'spinner', 
  width, 
  height, 
  count = 1 
}) => {
  if (type === 'spinner') {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '24px' }}>
        <Spinner />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', width: '100%' }}>
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton key={i} width={width} height={height} />
      ))}
    </div>
  );
};

export default Loader;
