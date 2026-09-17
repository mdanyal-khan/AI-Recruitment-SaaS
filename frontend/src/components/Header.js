import React, { useState, useEffect, useCallback, useRef } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { notificationsAPI } from '../services/api';
import './Header.css';

function Header() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [loadingNotifications, setLoadingNotifications] = useState(false);
  const dropdownRef = useRef(null);

  const fetchNotifications = useCallback(async () => {
    if (!user) return;
    try {
      setLoadingNotifications(true);
      const res = await notificationsAPI.list({ limit: 15 });
      const items = Array.isArray(res.data) ? res.data : [];
      setNotifications(items);
      const unread = items.filter((n) => n.status !== 'READ').length;
      setUnreadCount(unread);
    } catch (err) {
      console.error('Failed to load notifications:', err);
    } finally {
      setLoadingNotifications(false);
    }
  }, [user]);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000); // 30s auto-refresh
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMarkAsRead = async (id, e) => {
    e.stopPropagation();
    try {
      await notificationsAPI.markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, status: 'READ' } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/dashboard');
    }
  };

  // Don't show header on auth pages
  if (location.pathname === '/login' || location.pathname === '/register') {
    return null;
  }

  const initial = user?.first_name ? user.first_name[0].toUpperCase() : 'U';

  return (
    <header className="app-header">
      <div className="header-container">
        {/* Left Section - Logo */}
        <div className="header-left">
          {location.pathname !== '/dashboard' && (
            <button
              className="btn-back"
              onClick={handleBack}
              title="Go back"
              id="header-back-btn"
            >
              ←
            </button>
          )}
          <NavLink to="/dashboard" className="logo-link">
            <div className="logo-icon-spark">⚡</div>
            <div className="logo-text">
              <span className="logo-brand">SmartHire</span>
              <span className="logo-badge">AI</span>
            </div>
          </NavLink>
        </div>

        {/* Center - SPA Navigation */}
        <nav className="header-nav">
          <NavLink
            to="/dashboard"
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            Dashboard
          </NavLink>
          <NavLink
            to="/companies"
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            Companies
          </NavLink>
          <NavLink
            to="/jobs"
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            Jobs
          </NavLink>
          <NavLink
            to="/candidates"
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            Candidates
          </NavLink>
          <NavLink
            to="/matching"
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            AI Match
          </NavLink>
          <NavLink
            to="/interviews"
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            Interviews
          </NavLink>
          <NavLink
            to="/offers"
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            Offers
          </NavLink>
          <NavLink
            to="/resumes"
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            Resumes
          </NavLink>
        </nav>

        {/* Right Section - Notifications, User Chip & Logout */}
        <div className="header-right">
          {/* Notification Bell Dropdown */}
          <div className="notification-bell-wrapper" ref={dropdownRef}>
            <button
              className="btn-notification-bell"
              onClick={() => {
                setShowNotifications(!showNotifications);
                if (!showNotifications) fetchNotifications();
              }}
              title="Notifications"
              id="header-notifications-btn"
            >
              🔔
              {unreadCount > 0 && (
                <span className="notification-unread-badge">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>

            {showNotifications && (
              <div className="notification-dropdown-panel glass-card">
                <div className="notification-header">
                  <span className="notification-title">Notifications</span>
                  {unreadCount > 0 && (
                    <span className="notification-unread-tag">
                      {unreadCount} unread
                    </span>
                  )}
                </div>

                <div className="notification-list">
                  {loadingNotifications && notifications.length === 0 ? (
                    <div className="notification-empty">Loading notifications...</div>
                  ) : notifications.length === 0 ? (
                    <div className="notification-empty">No notifications yet</div>
                  ) : (
                    notifications.map((n) => (
                      <div
                        key={n.id}
                        className={`notification-item ${n.status === 'READ' ? 'is-read' : 'is-unread'}`}
                      >
                        <div className="notification-item-top">
                          <span className={`notification-type-badge type-${n.type?.toLowerCase()}`}>
                            {n.type?.replace(/_/g, ' ')}
                          </span>
                          <span className="notification-time">
                            {n.created_at ? new Date(n.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''}
                          </span>
                        </div>
                        <div className="notification-subject">{n.subject}</div>
                        {n.status !== 'READ' && (
                          <button
                            className="btn-mark-read"
                            onClick={(e) => handleMarkAsRead(n.id, e)}
                          >
                            Mark as read ✓
                          </button>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          {user && (
            <div className="user-profile-chip">
              <div className="user-avatar">{initial}</div>
              <div className="user-meta">
                <span className="user-name">{user.first_name || user.email}</span>
                <span className={`role-tag role-${user.role?.toLowerCase()}`}>
                  {user.role}
                </span>
              </div>
            </div>
          )}
          <button
            className="btn-logout"
            onClick={handleLogout}
            title="Sign out"
            id="header-logout-btn"
          >
            Sign out
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;
