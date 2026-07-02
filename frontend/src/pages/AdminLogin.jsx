import React, { useState, useRef, useEffect } from 'react';
import useAuthStore from '../store/useAuthStore';
import useAppStore from '../store/useAppStore';
import { ShieldCheck, Lock, LogIn, X, AlertTriangle } from 'lucide-react';
import './AdminLogin.css';

const AdminLogin = () => {
  const [password, setPassword] = useState('');
  const [shaking, setShaking] = useState(false);
  const { login, loading, error, clearError } = useAuthStore();
  const { setActivePage } = useAppStore();
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!password.trim()) return;

    try {
      await login(password);
      // On success, navigate to settings
      setActivePage('settings');
    } catch {
      // Trigger shake animation
      setShaking(true);
      setTimeout(() => setShaking(false), 500);
    }
  };

  const handleClose = () => {
    clearError();
    setActivePage('dashboard');
  };

  return (
    <div className="admin-login-overlay" onClick={handleClose}>
      <div
        className={`admin-login-card ${shaking ? 'admin-login-shake' : ''}`}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="admin-login-close"
          onClick={handleClose}
          aria-label="Close"
        >
          <X size={18} />
        </button>

        {/* Icon */}
        <div className="admin-login-icon-wrap">
          <ShieldCheck size={28} style={{ color: 'var(--color-accent-lime)' }} />
        </div>

        {/* Title */}
        <h2 className="admin-login-title">
          Admin <span style={{ color: 'var(--color-accent-lime)' }}>Access</span>
        </h2>
        <p className="admin-login-subtitle">
          Enter the admin password to unlock data management,<br />
          upload tools, and system settings.
        </p>

        {/* Form */}
        <form className="admin-login-form" onSubmit={handleSubmit}>
          {error && (
            <div className="admin-login-error">
              <AlertTriangle size={16} />
              {error}
            </div>
          )}

          <div className="admin-input-group">
            <label htmlFor="admin-password">Admin Password</label>
            <Lock size={16} className="admin-input-icon" />
            <input
              id="admin-password"
              ref={inputRef}
              type="password"
              className="admin-input"
              placeholder="Enter admin secret..."
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (error) clearError();
              }}
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="admin-login-submit"
            disabled={loading || !password.trim()}
          >
            <LogIn size={18} />
            {loading ? 'Authenticating...' : 'Unlock Admin Panel'}
          </button>
        </form>

        <p className="admin-login-footer">
          Admin access is required for data uploads and system configuration.
        </p>
      </div>
    </div>
  );
};

export default AdminLogin;
