import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { notificationsAPI } from '../../services/api';
import {
  Bell,
  Menu,
  Check,
  ChevronRight,
  Sparkles,
  Calendar,
  Award,
} from 'lucide-react';
import './Navbar.css';

const ROUTE_NAMES = {
  '/dashboard': 'Dashboard',
  '/jobs': 'Job Openings & Pipeline',
  '/candidates': 'Candidate Directory',
  '/matching': 'AI Matcher Studio',
  '/interviews': 'Interviews & Schedules',
  '/offers': 'Offers & Hiring Pipeline',
  '/resumes': 'Resume Intelligence Pool',
  '/companies': 'Company Workspace',
  '/admin/system': 'System Health',
};

export default function Navbar({ onMobileMenuToggle }) {
  const location = useLocation();
  const { user } = useAuth();

  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const dropdownRef = useRef(null);

  const fetchNotifications = useCallback(async () => {
    if (!user) return;
    try {
      const res = await notificationsAPI.list({ limit: 10 });
      const items = Array.isArray(res.data) ? res.data : [];
      setNotifications(items);
      const unread = items.filter((n) => n.status !== 'READ').length;
      setUnreadCount(unread);
    } catch (err) {
      // Non-fatal
    }
  }, [user]);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
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
      // Non-fatal
    }
  };

  const currentTitle = ROUTE_NAMES[location.pathname] || 'Workspace';

  return (
    <header className="app-navbar">
      {/* Left: Mobile menu toggle + Breadcrumbs */}
      <div className="navbar-left">
        <button
          type="button"
          className="navbar-mobile-toggle"
          onClick={onMobileMenuToggle}
          aria-label="Toggle navigation menu"
        >
          <Menu size={20} />
        </button>

        <div className="navbar-breadcrumbs">
          <Link to="/dashboard" className="breadcrumb-root">Home</Link>
          <ChevronRight size={14} className="breadcrumb-separator" />
          <span className="breadcrumb-current">{currentTitle}</span>
        </div>
      </div>

      {/* Right: Notifications & User Profile */}
      <div className="navbar-right">
        {/* Notifications Dropdown */}
        <div className="notification-wrapper" ref={dropdownRef}>
          <button
            type="button"
            className="navbar-icon-btn"
            onClick={() => setShowNotifications(!showNotifications)}
            aria-label="Notifications"
          >
            <Bell size={18} />
            {unreadCount > 0 && (
              <span className="notification-badge-dot">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {showNotifications && (
            <div className="notification-popover">
              <div className="popover-header">
                <h4>Notifications</h4>
                {unreadCount > 0 && (
                  <span className="unread-counter">{unreadCount} unread</span>
                )}
              </div>

              <div className="popover-list">
                {notifications.length === 0 ? (
                  <div className="popover-empty">
                    <p>No notifications yet</p>
                  </div>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      className={`notification-item ${
                        n.status !== 'READ' ? 'item-unread' : ''
                      }`}
                    >
                      <div className="notif-icon-type">
                        {n.type === 'OFFER' ? (
                          <Award size={14} className="icon-gold" />
                        ) : n.type === 'INTERVIEW_INVITATION' ? (
                          <Calendar size={14} className="icon-blue" />
                        ) : (
                          <Sparkles size={14} className="icon-purple" />
                        )}
                      </div>
                      <div className="notif-content">
                        <div className="notif-title">{n.title}</div>
                        <div className="notif-message">{n.message}</div>
                        <div className="notif-time">
                          {new Date(n.created_at).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </div>
                      </div>
                      {n.status !== 'READ' && (
                        <button
                          type="button"
                          className="btn-mark-read"
                          onClick={(e) => handleMarkAsRead(n.id, e)}
                          title="Mark as read"
                        >
                          <Check size={12} />
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Identity Chip */}
        <div className="navbar-user-chip">
          <div className="navbar-avatar">
            {user?.first_name ? user.first_name[0].toUpperCase() : 'U'}
          </div>
          <span className="navbar-username">
            {user?.first_name ? `${user.first_name}` : 'User'}
          </span>
        </div>
      </div>
    </header>
  );
}
