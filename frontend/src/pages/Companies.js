import React, { useState, useEffect } from 'react';
import { companiesAPI, formatApiError } from '../services/api';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Modal from '../components/ui/Modal';
import EmptyState from '../components/ui/EmptyState';
import { Input, Textarea } from '../components/ui/Input';
import {
  Building,
  Plus,
  Globe,
  MapPin,
  Users,
  Trash2,
} from 'lucide-react';
import './Page.css';

export default function Companies() {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    website: '',
    industry: 'Software & Tech',
    location: '',
    logo_url: '',
  });

  // Members state
  const [selectedCompanyForMembers, setSelectedCompanyForMembers] = useState(null);
  const [members, setMembers] = useState([]);
  const [loadingMembers, setLoadingMembers] = useState(false);
  const [newMemberEmail, setNewMemberEmail] = useState('');
  const [newMemberRole, setNewMemberRole] = useState('RECRUITER');
  const [addingMember, setAddingMember] = useState(false);

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await companiesAPI.list();
      setCompanies(response.data || []);
    } catch (err) {
      setError('Failed to load your companies.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      setError('');
      await companiesAPI.create(formData);
      setSuccess('Company created successfully! You are assigned as OWNER.');
      setFormData({
        name: '',
        description: '',
        website: '',
        industry: 'Software & Tech',
        location: '',
        logo_url: '',
      });
      setShowForm(false);
      fetchCompanies();
    } catch (err) {
      setError(formatApiError(err, 'Failed to create company.'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleOpenMembers = async (company) => {
    setSelectedCompanyForMembers(company);
    setLoadingMembers(true);
    try {
      const res = await companiesAPI.getMembers(company.id);
      setMembers(res.data || []);
    } catch (err) {
      setError('Failed to load team members');
    } finally {
      setLoadingMembers(false);
    }
  };

  const handleAddMember = async (e) => {
    e.preventDefault();
    if (!selectedCompanyForMembers || !newMemberEmail) return;

    try {
      setAddingMember(true);
      await companiesAPI.addMember(selectedCompanyForMembers.id, {
        email: newMemberEmail,
        role: newMemberRole,
      });
      setSuccess(`Team member added: ${newMemberEmail}`);
      setNewMemberEmail('');
      const res = await companiesAPI.getMembers(selectedCompanyForMembers.id);
      setMembers(res.data || []);
    } catch (err) {
      setError(formatApiError(err, 'Failed to add member'));
    } finally {
      setAddingMember(false);
    }
  };

  const handleRemoveMember = async (userId) => {
    if (!window.confirm('Remove this member from the company workspace?')) return;
    try {
      await companiesAPI.removeMember(selectedCompanyForMembers.id, userId);
      setSuccess('Member removed.');
      const res = await companiesAPI.getMembers(selectedCompanyForMembers.id);
      setMembers(res.data || []);
    } catch (err) {
      setError(formatApiError(err, 'Failed to remove member'));
    }
  };

  return (
    <div className="page-shell">
      {/* Header */}
      <div className="page-header-row">
        <div>
          <h1 className="page-title">Company Workspaces</h1>
          <p className="page-subtitle">
            Configure employer branding, recruitment settings, and manage team recruiter permissions.
          </p>
        </div>

        <div className="page-actions-row">
          <Button
            variant="primary"
            size="md"
            icon={Plus}
            onClick={() => setShowForm(true)}
          >
            Create Company
          </Button>
        </div>
      </div>

      {error && <div className="alert alert-error"><span>⚠️ {error}</span></div>}
      {success && <div className="alert alert-success"><span>✓ {success}</span></div>}

      {/* Companies Grid */}
      {loading ? (
        <p style={{ textAlign: 'center', padding: '32px' }}>Loading company workspaces...</p>
      ) : companies.length === 0 ? (
        <EmptyState
          icon={Building}
          title="No companies found"
          description="Create your company workspace to publish job postings and assemble a recruitment team."
          actionLabel="Create Company"
          onAction={() => setShowForm(true)}
        />
      ) : (
        <div className="card-grid">
          {companies.map((comp) => (
            <Card key={comp.id} hover>
              <Card.Header>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div
                      style={{
                        width: '44px',
                        height: '44px',
                        borderRadius: 'var(--radius-lg)',
                        backgroundColor: 'var(--brand-50)',
                        color: 'var(--brand-600)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 700,
                        fontSize: '1.25rem',
                      }}
                    >
                      {comp.name[0]}
                    </div>
                    <div>
                      <Card.Title>{comp.name}</Card.Title>
                      <Card.Description>{comp.industry || 'Software & Tech'}</Card.Description>
                    </div>
                  </div>
                  <span className="status-badge badge-neutral">Active</span>
                </div>
              </Card.Header>

              <Card.Content>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                  {comp.description || 'No description provided.'}
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.8125rem' }}>
                  {comp.location && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)' }}>
                      <MapPin size={14} /> <span>{comp.location}</span>
                    </div>
                  )}
                  {comp.website && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Globe size={14} className="text-brand" />
                      <a href={comp.website} target="_blank" rel="noopener noreferrer">
                        {comp.website.replace(/^https?:\/\//, '')}
                      </a>
                    </div>
                  )}
                </div>
              </Card.Content>

              <Card.Footer>
                <Button
                  variant="secondary"
                  size="sm"
                  icon={Users}
                  onClick={() => handleOpenMembers(comp)}
                  style={{ width: '100%' }}
                >
                  Manage Team Members
                </Button>
              </Card.Footer>
            </Card>
          ))}
        </div>
      )}

      {/* Create Company Modal */}
      <Modal
        isOpen={showForm}
        onClose={() => setShowForm(false)}
        title="Create Company Workspace"
        subtitle="You will be designated as the OWNER of this workspace"
        maxWidth="540px"
      >
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group full-width">
              <Input
                label="Company Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="e.g. Acme Technologies Inc."
                required
              />
            </div>
            <div className="form-group full-width">
              <Textarea
                label="Company Overview"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={3}
                placeholder="Brief mission and products summary..."
              />
            </div>
            <Input
              label="Official Website"
              name="website"
              value={formData.website}
              onChange={handleChange}
              placeholder="https://acme.com"
            />
            <Input
              label="Industry / Domain"
              name="industry"
              value={formData.industry}
              onChange={handleChange}
            />
            <div className="form-group full-width">
              <Input
                label="Headquarters Location"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="San Francisco, CA or Remote"
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' }}>
            <Button variant="secondary" onClick={() => setShowForm(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={submitting}>
              Create Company
            </Button>
          </div>
        </form>
      </Modal>

      {/* Team Members Modal */}
      <Modal
        isOpen={Boolean(selectedCompanyForMembers)}
        onClose={() => setSelectedCompanyForMembers(null)}
        title={`Team Members: ${selectedCompanyForMembers?.name || 'Company'}`}
        subtitle="Invite team recruiters or managers to collaborate on job postings"
        maxWidth="540px"
      >
        {/* Add Member Form */}
        <form onSubmit={handleAddMember} style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            <div style={{ flex: 1 }}>
              <input
                type="email"
                placeholder="user@company.com"
                value={newMemberEmail}
                onChange={(e) => setNewMemberEmail(e.target.value)}
                required
                className="input-control"
              />
            </div>
            <select
              value={newMemberRole}
              onChange={(e) => setNewMemberRole(e.target.value)}
              className="select-control"
              style={{ width: '130px' }}
            >
              <option value="RECRUITER">Recruiter</option>
              <option value="HR">HR</option>
              <option value="COMPANY_ADMIN">Admin</option>
            </select>
            <Button type="submit" variant="primary" size="md" loading={addingMember}>
              Add
            </Button>
          </div>
        </form>

        {/* Member List */}
        {loadingMembers ? (
          <p style={{ textAlign: 'center', padding: '24px' }}>Loading members...</p>
        ) : members.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>No team members assigned yet.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {members.map((m) => (
              <div
                key={m.user_id || m.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 14px',
                  backgroundColor: 'var(--bg-surface-subtle)',
                  borderRadius: 'var(--radius-md)',
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>
                    {m.email || m.user?.email || 'Team Member'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Role: {m.role}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => handleRemoveMember(m.user_id || m.id)}
                  style={{ color: 'var(--danger-500)', padding: '6px' }}
                  title="Remove member"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </Modal>
    </div>
  );
}
