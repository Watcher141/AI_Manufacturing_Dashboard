import React from 'react';
import './ui.css';

const Button = ({ 
  children, 
  variant = 'primary', 
  onClick, 
  disabled = false, 
  type = 'button',
  style = {} 
}) => {
  const getClassName = () => {
    if (disabled) return 'btn btn-disabled';
    switch (variant) {
      case 'primary': return 'btn btn-primary';
      case 'inverted': return 'btn btn-inverted';
      case 'ghost': return 'btn btn-ghost-on-dark';
      case 'violet-token': return 'btn btn-violet-token';
      default: return 'btn btn-primary';
    }
  };

  return (
    <button 
      type={type} 
      className={getClassName()} 
      onClick={onClick} 
      disabled={disabled}
      style={style}
    >
      {children}
    </button>
  );
};

export default Button;
