import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  candidatesAPI,
  companiesAPI,
  hrApplicationsAPI,
  formatApiError,
} from '../services/api';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Modal from '../components/ui/Modal';
import EmptyState from '../components/ui/EmptyState';
import StatusBadge from '../components/ui/StatusBadge';
import { Input, Textarea } from '../components/ui/Input';
import {
  User,
  MapPin,
  Phone,
  Globe,
  ExternalLink,
  Briefcase,
  Edit2,
  Users,
  Search,
  Mail,
  Calendar,
  Sparkles,
  ArrowRight,
} from 'lucide-react';
import './Page.css';

export default function Candidates() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const isRecruiter = ['OWNER', 'HR', 'RECRUITER', 'COMPANY_ADMIN'].includes(
    user?.role?.toUpperCase()
  );

  // Tab mode for Recruiters: 'TALENT_POOL' or 'MY_PORTFOLIO'
  const [activeTab, setActiveTab] = useState('TALENT_POOL');

  // Recruiter Talent Pool State
  const [companies, setCompanies] = useState([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState('');
  const [talentPool, setTalentPool] = useState([]);
  const [loadingPool, setLoadingPool] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Personal Profile State
  const [profile, setProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    headline: '',
    summary: '',
    location: '',
    phone: '',
    linkedin_url: '',
    github_url: '',
    portfolio_url: '',
    years_experience: 0,
  });

  // Fetch HR Talent Pool Candidates
  const fetchTalentPool = useCallback(async (companyId, status = 'ALL') => {
    if (!companyId) return;
    try {
      setLoadingPool(true);
      setError('');
      const res = await hrApplicationsAPI.getAllApplications(
        companyId,
        status === 'ALL' ? undefined : status
      );
      setTalentPool(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      setTalentPool([]);
    } finally {
      setLoadingPool(false);
    }
  }, []);

  // Fetch Companies for Recruiter
  useEffect(() => {
    if (!isRecruiter) return;
    const loadCompanies = async () => {
      try {
        const res = await companiesAPI.list();
        const list = res.data || [];
        setCompanies(list);
        if (list.length > 0) {
          setSelectedCompanyId(list[0].id);
          fetchTalentPool(list[0].id, statusFilter);
        }
      } catch (err) {
        // Handled silently
      }
    };
    loadCompanies();
  }, [isRecruiter, fetchTalentPool, statusFilter]);

  // Fetch Personal Profile
  const fetchProfile = useCallback(async () => {
    try {
      setLoadingProfile(true);
      setError('');
      const response = await candidatesAPI.getProfile();
      const d = response.data;
      setProfile(d);
      setFormData({
        headline: d.headline || '',
        summary: d.summary || '',
        location: d.location || '',
        phone: d.phone || '',
        linkedin_url: d.linkedin_url || '',
        github_url: d.github_url || '',
        portfolio_url: d.portfolio_url || '',
        years_experience:
          d.years_experience !== null ? Number(d.years_experience) : 0,
      });
    } catch (err) {
      if (err.response?.status === 404) {
        setProfile(null);
      } else {
        if (!isRecruiter) {
          setError('Failed to fetch candidate portfolio.');
        }
      }
    } finally {
      setLoadingProfile(false);
    }
  }, [isRecruiter]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const handleCompanyChange = (e) => {
    const compId = e.target.value;
    setSelectedCompanyId(compId);
    fetchTalentPool(compId, statusFilter);
  };

  const handleStatusFilterChange = (status) => {
    setStatusFilter(status);
    if (selectedCompanyId) {
      fetchTalentPool(selectedCompanyId, status);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'years_experience' ? parseFloat(value) || 0 : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      setError('');
      setSuccess('');
      if (profile) {
        await candidatesAPI.updateProfile(formData);
        setSuccess('Portfolio updated successfully!');
      } else {
        await candidatesAPI.createProfile(formData);
        setSuccess('Portfolio created successfully!');
      }
      setIsEditing(false);
      fetchProfile();
    } catch (err) {
      setError(formatApiError(err, 'Failed to save portfolio'));
    } finally {
      setSubmitting(false);
    }
  };

  // Filter talent pool by search query
  const filteredCandidates = talentPool.filter((c) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const nameMatch = c.candidate_name?.toLowerCase().includes(q);
    const emailMatch = c.candidate_email?.toLowerCase().includes(q);
    const jobMatch = c.job_title?.toLowerCase().includes(q);
    return nameMatch || emailMatch || jobMatch;
  });

  return (
    <div className="page-shell">
      {/* Page Header */}
      <div className="page-header-row">
        <div>
          <h1 className="page-title">
            {isRecruiter
              ? activeTab === 'TALENT_POOL'
                ? 'Candidate Talent Pool'
                : 'My Professional Portfolio'
              : 'My Professional Portfolio'}
          </h1>
          <p className="page-subtitle">
            {isRecruiter
              ? activeTab === 'TALENT_POOL'
                ? 'Inspect, search, and manage candidate applicants across all your active company job openings.'
                : 'Manage your individual profile and portfolio details.'
              : 'Showcase your background, skills, portfolio projects, and social links to hiring teams.'}
          </p>
        </div>

        <div className="page-actions-row">
          {/* Recruiter Tab Toggle */}
          {isRecruiter && (
            <div style={{ display: 'flex', gap: '8px' }}>
              <Button
                variant={activeTab === 'TALENT_POOL' ? 'primary' : 'secondary'}
                size="sm"
                icon={Users}
                onClick={() => setActiveTab('TALENT_POOL')}
              >
                Talent Pool
              </Button>
              <Button
                variant={activeTab === 'MY_PORTFOLIO' ? 'primary' : 'secondary'}
                size="sm"
                icon={User}
                onClick={() => setActiveTab('MY_PORTFOLIO')}
              >
                My Portfolio
              </Button>
            </div>
          )}

          {/* Edit Profile button when on portfolio view */}
          {(!isRecruiter || activeTab === 'MY_PORTFOLIO') && (
            <Button
              variant={profile ? 'secondary' : 'primary'}
              size="md"
              icon={Edit2}
              onClick={() => setIsEditing(true)}
            >
              {profile ? 'Edit Portfolio' : 'Create Portfolio'}
            </Button>
          )}

          {/* Company Workspace selector for recruiter */}
          {isRecruiter && activeTab === 'TALENT_POOL' && companies.length > 0 && (
            <select
              value={selectedCompanyId}
              onChange={handleCompanyChange}
              className="select-control"
              style={{ width: 'auto', minWidth: '200px' }}
            >
              {companies.map((c) => (
                <option key={c.id} value={c.id}>
                  🏢 {c.name}
                </option>
              ))}
            </select>
          )}
        </div>
      </div>

      {/* Alerts */}
      {error && <div className="alert alert-error"><span>⚠️ {error}</span></div>}
      {success && <div className="alert alert-success"><span>✓ {success}</span></div>}

      {/* ==================================================== */}
      {/* 1. RECRUITER TALENT POOL VIEW                        */}
      {/* ==================================================== */}
      {isRecruiter && activeTab === 'TALENT_POOL' ? (
        <div>
          {/* Search & Status Filters */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '16px',
              marginBottom: '20px',
            }}
          >
            <div style={{ width: '320px' }}>
              <Input
                icon={Search}
                placeholder="Search candidate name, email, or role..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className="filter-bar" style={{ marginBottom: 0 }}>
              {[
                'ALL',
                'APPLIED',
                'SHORTLISTED',
                'INTERVIEWING',
                'OFFERED',
                'HIRED',
                'REJECTED',
              ].map((st) => (
                <button
                  key={st}
                  type="button"
                  className={`filter-tab ${statusFilter === st ? 'active' : ''}`}
                  onClick={() => handleStatusFilterChange(st)}
                >
                  {st === 'ALL' ? 'All Applicants' : st}
                </button>
              ))}
            </div>
          </div>

          {/* Candidates Grid */}
          {loadingPool ? (
            <p style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
              Loading candidate talent pool...
            </p>
          ) : filteredCandidates.length === 0 ? (
            <EmptyState
              icon={Users}
              title="No candidates found"
              description={
                searchQuery || statusFilter !== 'ALL'
                  ? 'No candidates match your search and filter criteria.'
                  : 'No candidate applications submitted for this company workspace yet.'
              }
              actionLabel="Explore Published Openings"
              onAction={() => navigate('/jobs')}
            />
          ) : (
            <div className="card-grid">
              {filteredCandidates.map((c) => (
                <Card key={c.application_id} hover className="job-card-item">
                  <Card.Header>
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div
                          style={{
                            width: '42px',
                            height: '42px',
                            borderRadius: 'var(--radius-full)',
                            backgroundColor: 'var(--brand-100)',
                            color: 'var(--brand-700)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontWeight: 700,
                            fontSize: '1rem',
                          }}
                        >
                          {c.candidate_name ? c.candidate_name[0].toUpperCase() : 'C'}
                        </div>
                        <div>
                          <Card.Title style={{ fontSize: '1.05rem' }}>
                            {c.candidate_name || 'Anonymous Candidate'}
                          </Card.Title>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)', fontSize: '0.8125rem', marginTop: '2px' }}>
                            <Mail size={12} />
                            <span>{c.candidate_email || 'No email provided'}</span>
                          </div>
                        </div>
                      </div>
                      <StatusBadge status={c.application_status} />
                    </div>
                  </Card.Header>

                  <Card.Content>
                    <div style={{ padding: '10px 12px', background: 'var(--bg-subtle, rgba(255,255,255,0.03))', borderRadius: '8px', border: '1px solid var(--border-subtle)', marginBottom: '12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                        <Briefcase size={14} className="text-brand" />
                        <span>{c.job_title}</span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.8125rem' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--text-muted)' }}>
                        <Calendar size={13} />
                        {c.applied_at
                          ? new Date(c.applied_at).toLocaleDateString(undefined, {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric',
                            })
                          : 'Recent'}
                      </span>

                      {c.match_score !== null && c.match_score !== undefined ? (
                        <span
                          className={`status-badge ${
                            c.match_score >= 70
                              ? 'badge-success'
                              : c.match_score >= 50
                              ? 'badge-warning'
                              : 'badge-error'
                          }`}
                          style={{ fontSize: '0.75rem', padding: '3px 8px' }}
                        >
                          <Sparkles size={12} /> {Math.round(c.match_score)}% Match
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                          Awaiting Screening
                        </span>
                      )}
                    </div>
                  </Card.Content>

                  <Card.Footer>
                    <div style={{ display: 'flex', gap: '8px', width: '100%', justifyContent: 'space-between' }}>
                      <Button
                        variant="secondary"
                        size="sm"
                        icon={Sparkles}
                        onClick={() => navigate('/matching')}
                        title="Evaluate candidate in AI Matcher"
                      >
                        AI Match
                      </Button>
                      <Button
                        variant="primary"
                        size="sm"
                        icon={ArrowRight}
                        onClick={() => navigate('/jobs')}
                      >
                        Pipeline View
                      </Button>
                    </div>
                  </Card.Footer>
                </Card>
              ))}
            </div>
          )}
        </div>
      ) : (
        /* ==================================================== */
        /* 2. PERSONAL PORTFOLIO VIEW                           */
        /* ==================================================== */
        <div>
          {loadingProfile ? (
            <p style={{ textAlign: 'center', padding: '32px' }}>
              Loading portfolio profile...
            </p>
          ) : !profile ? (
            <EmptyState
              icon={User}
              title="No portfolio created yet"
              description="Build your professional candidate portfolio to showcase your skills, projects, and career credentials."
              actionLabel="Create Portfolio Now"
              onAction={() => setIsEditing(true)}
            />
          ) : (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                gap: '24px',
              }}
            >
              {/* Main Info Card */}
              <Card style={{ gridColumn: '1 / -1' }}>
                <Card.Header>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div
                      style={{
                        width: '64px',
                        height: '64px',
                        borderRadius: 'var(--radius-full)',
                        backgroundColor: 'var(--brand-100)',
                        color: 'var(--brand-700)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '1.5rem',
                        fontWeight: 700,
                      }}
                    >
                      <User size={32} />
                    </div>
                    <div>
                      <Card.Title style={{ fontSize: '1.5rem' }}>
                        {profile.headline || 'Professional Candidate'}
                      </Card.Title>
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '16px',
                          marginTop: '6px',
                          color: 'var(--text-secondary)',
                          fontSize: '0.875rem',
                          flexWrap: 'wrap',
                        }}
                      >
                        {profile.location && (
                          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <MapPin size={14} /> {profile.location}
                          </span>
                        )}
                        {profile.phone && (
                          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <Phone size={14} /> {profile.phone}
                          </span>
                        )}
                        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Briefcase size={14} /> {profile.years_experience} Years Experience
                        </span>
                      </div>
                    </div>
                  </div>
                </Card.Header>

                <Card.Content>
                  <h4
                    style={{
                      fontSize: '0.875rem',
                      fontWeight: 600,
                      color: 'var(--text-secondary)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.04em',
                      marginBottom: '8px',
                    }}
                  >
                    Professional Summary
                  </h4>
                  <p
                    style={{
                      color: 'var(--text-primary)',
                      fontSize: '0.9375rem',
                      lineHeight: 1.6,
                    }}
                  >
                    {profile.summary ||
                      'No summary provided yet. Click Edit Portfolio to add your career summary.'}
                  </p>

                  {/* Portfolio Links Row */}
                  <div
                    style={{
                      display: 'flex',
                      gap: '16px',
                      marginTop: '20px',
                      flexWrap: 'wrap',
                    }}
                  >
                    {profile.linkedin_url && (
                      <a
                        href={profile.linkedin_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="status-badge badge-info"
                        style={{ textDecoration: 'none', padding: '6px 12px' }}
                      >
                        <ExternalLink size={14} /> LinkedIn Profile
                      </a>
                    )}
                    {profile.github_url && (
                      <a
                        href={profile.github_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="status-badge badge-neutral"
                        style={{ textDecoration: 'none', padding: '6px 12px' }}
                      >
                        <ExternalLink size={14} /> GitHub Repository
                      </a>
                    )}
                    {profile.portfolio_url && (
                      <a
                        href={profile.portfolio_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="status-badge badge-ai"
                        style={{ textDecoration: 'none', padding: '6px 12px' }}
                      >
                        <Globe size={14} /> Personal Portfolio / Website
                      </a>
                    )}
                  </div>
                </Card.Content>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* Edit Profile Modal */}
      <Modal
        isOpen={isEditing}
        onClose={() => setIsEditing(false)}
        title={profile ? 'Update Professional Portfolio' : 'Create Professional Portfolio'}
        subtitle="Credentials will be indexed for automated matching and recruitment evaluations"
        maxWidth="600px"
      >
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group full-width">
              <Input
                label="Professional Headline"
                name="headline"
                value={formData.headline}
                onChange={handleChange}
                placeholder="e.g. Senior Full-Stack Engineer | AI & Cloud Architecture"
                required
              />
            </div>

            <div className="form-group full-width">
              <Textarea
                label="Executive Career Summary"
                name="summary"
                value={formData.summary}
                onChange={handleChange}
                rows={4}
                placeholder="Overview of your background, core competencies, and career achievements..."
                required
              />
            </div>

            <Input
              label="Location"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="e.g. San Francisco, CA or Remote"
            />

            <Input
              label="Phone Number"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="+1 (555) 000-0000"
            />

            <Input
              label="Years of Experience"
              name="years_experience"
              type="number"
              step="0.5"
              value={formData.years_experience}
              onChange={handleChange}
            />

            <Input
              label="LinkedIn URL"
              name="linkedin_url"
              value={formData.linkedin_url}
              onChange={handleChange}
              placeholder="https://linkedin.com/in/username"
            />

            <Input
              label="GitHub URL"
              name="github_url"
              value={formData.github_url}
              onChange={handleChange}
              placeholder="https://github.com/username"
            />

            <Input
              label="Portfolio / Website URL"
              name="portfolio_url"
              value={formData.portfolio_url}
              onChange={handleChange}
              placeholder="https://yourportfolio.dev"
            />
          </div>

          <div
            style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '12px',
              marginTop: '20px',
            }}
          >
            <Button variant="secondary" onClick={() => setIsEditing(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={submitting}>
              Save Portfolio
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
