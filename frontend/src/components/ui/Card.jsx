import React from 'react';
import './ui.css';

const Card = ({ 
  children, 
  variant = 'dark', 
  className = '', 
  style = {} 
}) => {
  const getClassName = () => {
    let base = 'card';
    if (variant === 'light') base += ' card-light';
    else if (variant === 'feature') base += ' card-feature-dark';
    else if (variant === 'spotlight') base += ' card-spotlight-violet';
    return `${base} ${className}`;
  };

  return (
    <div className={getClassName()} style={style}>
      {children}
    </div>
  );
};

export default Card;
