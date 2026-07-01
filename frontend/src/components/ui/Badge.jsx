import React from 'react';
import './ui.css';

const Badge = ({ 
  children, 
  status = 'info' 
}) => {
  const getClassName = () => {
    const s = status ? status.toLowerCase() : 'info';
    return `badge badge-${s}`;
  };

  return (
    <span className={getClassName()}>
      {children}
    </span>
  );
};

export default Badge;
