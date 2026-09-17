import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  Briefcase,
  Users,
  FileText,
  Sparkles,
  Calendar,
  Award,
  Building,
  Activity,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import './Sidebar.css';

export default function Sidebar({ collapsed, setCollapsed, isMobile, mobileOpen, setMobileOpen }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const isRecruiter = ['OWNER', 'HR', 'RECRUITER', 'COMPANY_ADMIN'].includes(user?.role?.toUpperCase());

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = isRecruiter
    ? [
        { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { to: '/jobs', label: 'Jobs & Pipeline', icon: Briefcase },
        { to: '/candidates', label: 'Candidates Pool', icon: Users },
        { to: '/matching', label: 'AI Matcher', icon: Sparkles, badge: 'AI' },
        { to: '/interviews', label: 'Interviews', icon: Calendar },
        { to: '/offers', label: 'Offers & Hires', icon: Award },
        { to: '/resumes', label: 'Resumes Pool', icon: FileText },
        { to: '/companies', label: 'Company Workspace', icon: Building },
        { to: '/admin/system', label: 'System Health', icon: Activity },
      ]
    : [
        { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { to: '/jobs', label: 'Find Jobs', icon: Briefcase },
        { to: '/resumes', label: 'My Resume (AI)', icon: FileText, badge: 'CV' },
        { to: '/interviews', label: 'My Interviews', icon: Calendar },
        { to: '/offers', label: 'My Offers', icon: Award },
        { to: '/candidates', label: 'My Portfolio', icon: Users },
        { to: '/matching', label: 'Job Matching', icon: Sparkles, badge: 'AI' },
      ];

  const handleNavClick = () => {
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  return (
    <aside
      className={`app-sidebar ${collapsed ? 'sidebar-collapsed' : ''} ${
        isMobile ? (mobileOpen ? 'sidebar-mobile-open' : 'sidebar-mobile-closed') : ''
      }`}
    >
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="brand-logo-spark">⚡</div>
        {!collapsed && (
          <div className="brand-info">
            <span className="brand-title">SmartHire</span>
            <span className="brand-badge-tag">AI SaaS</span>
          </div>
        )}
        {!isMobile && (
          <button
            type="button"
            className="sidebar-collapse-btn"
            onClick={() => setCollapsed(!collapsed)}
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        )}
      </div>

      {/* Navigation List */}
      <nav className="sidebar-nav">
        <div className="sidebar-section-label">
          {!collapsed ? (isRecruiter ? 'Recruitment Hub' : 'Candidate Portal') : '•••'}
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={handleNavClick}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'sidebar-link-active' : ''}`
              }
              title={collapsed ? item.label : undefined}
            >
              <div className="link-icon-wrap">
                <Icon size={18} />
              </div>
              {!collapsed && (
                <span className="link-label">
                  {item.label}
                  {item.badge && <span className="nav-item-badge">{item.badge}</span>}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* User & Workspace Footer */}
      <div className="sidebar-footer">
        <div className="user-profile-widget">
          <div className="user-avatar-circle">
            {user?.first_name ? user.first_name[0].toUpperCase() : 'U'}
          </div>
          {!collapsed && (
            <div className="user-text-info">
              <span className="user-name">
                {user?.first_name ? `${user.first_name} ${user.last_name || ''}` : 'User Account'}
              </span>
              <span className="user-role-chip">
                {user?.role || 'MEMBER'}
              </span>
            </div>
          )}
          <button
            type="button"
            className="btn-sidebar-logout"
            onClick={handleLogout}
            title="Sign out"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
}
