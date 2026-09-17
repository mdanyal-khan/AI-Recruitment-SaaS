import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  companiesAPI,
  jobsAPI,
  applicationsAPI,
  interviewsAPI,
  hrApplicationsAPI,
  screeningAPI,
  offersAPI,
  hiringAPI,
  formatApiError,
} from '../services/api';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import StatusBadge from '../components/ui/StatusBadge';
import { ScoreCircle } from '../components/ui/ScoreIndicator';
import Modal from '../components/ui/Modal';
import Drawer from '../components/ui/Drawer';
import EmptyState from '../components/ui/EmptyState';
import AIScreeningCard from '../components/ai/AIScreeningCard';
import { Input, Select, Textarea } from '../components/ui/Input';
import {
  Briefcase,
  Plus,
  Search,
  Users,
  Sparkles,
  Calendar,
  Award,
  MapPin,
  DollarSign,
} from 'lucide-react';
import './Page.css';

export default function Jobs() {
  const { user } = useAuth();
  const isRecruiter = ['OWNER', 'HR', 'RECRUITER', 'COMPANY_ADMIN'].includes(
    user?.role?.toUpperCase()
  );

  const [companies, setCompanies] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Filtering & Search
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Create Job Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creatingJob, setCreatingJob] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: 'Remote',
    employment_type: 'FULL_TIME',
    experience_min: 1,
    experience_max: 5,
    education_level: 'BACHELOR',
    salary_min: 60000,
    salary_max: 120000,
    deadline: '',
  });

  // Applicants Drawer / Modal
  const [selectedJobForApplicants, setSelectedJobForApplicants] = useState(null);
  const [applicantsData, setApplicantsData] = useState([]);
  const [loadingApplicants, setLoadingApplicants] = useState(false);
  const [applicantStatusFilter, setApplicantStatusFilter] = useState('ALL');

  // AI Screening Detail
  const [screeningAppId, setScreeningAppId] = useState(null);
  const [detailedApp, setDetailedApp] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  // Schedule Interview Modal
  const [schedulingApp, setSchedulingApp] = useState(null);
  const [schedulingLoading, setSchedulingLoading] = useState(false);
  const [interviewForm, setInterviewForm] = useState({
    start_time: '',
    end_time: '',
    mode: 'ONLINE',
    meeting_url: 'https://meet.google.com/smarthire-interview',
    location: '',
  });

  // Make Offer Modal
  const [offerModalApp, setOfferModalApp] = useState(null);
  const [creatingOffer, setCreatingOffer] = useState(false);
  const [offerForm, setOfferForm] = useState({
    salary: 100000,
    currency: 'USD',
    start_date: '',
    expiration_date: '',
    notes: '',
  });

  // Candidate Apply State
  const [applyingJobId, setApplyingJobId] = useState(null);

  const fetchJobs = useCallback(async (companyId) => {
    try {
      setLoading(true);
      setError('');
      const response = await jobsAPI.list(companyId);
      setJobs(response.data || []);
    } catch (err) {
      setJobs([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchCompanies = useCallback(async () => {
    if (!isRecruiter) {
      try {
        setLoading(true);
        setError('');
        const response = await jobsAPI.listPublished();
        setJobs(response.data || []);
      } catch (err) {
        setJobs([]);
        setError(formatApiError(err, 'Failed to fetch jobs'));
      } finally {
        setLoading(false);
      }
      return;
    }

    try {
      setLoading(true);
      const response = await companiesAPI.list();
      const data = response.data || [];
      setCompanies(data);
      if (data.length > 0) {
        setSelectedCompanyId(data[0].id);
        fetchJobs(data[0].id);
      }
    } catch (err) {
      setError('Failed to fetch companies. Please create or join a company first.');
    } finally {
      setLoading(false);
    }
  }, [fetchJobs, isRecruiter]);

  useEffect(() => {
    fetchCompanies();
  }, [fetchCompanies]);

  const handleCompanyChange = (e) => {
    const companyId = e.target.value;
    setSelectedCompanyId(companyId);
    if (companyId) {
      fetchJobs(companyId);
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        name.includes('min') || name.includes('max')
          ? parseInt(value) || 0
          : value,
    }));
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    let companyId = selectedCompanyId;
    if (!companyId && companies.length > 0) {
      companyId = companies[0].id;
      setSelectedCompanyId(companyId);
    }
    if (!companyId) {
      try {
        const compRes = await companiesAPI.list();
        const list = compRes.data || [];
        if (list.length > 0) {
          companyId = list[0].id;
          setCompanies(list);
          setSelectedCompanyId(companyId);
        }
      } catch (e) {
        // Fallback handled below
      }
    }

    if (!companyId) {
      setError('Please create or select a company workspace first to post this job.');
      return;
    }

    try {
      setCreatingJob(true);
      setError('');
      const payload = {
        ...formData,
        deadline: formData.deadline || null,
      };
      await jobsAPI.create(companyId, payload);
      setSuccess('Job created & analyzed! Starts in DRAFT status.');
      setShowCreateModal(false);
      setFormData({
        title: '',
        description: '',
        location: 'Remote',
        employment_type: 'FULL_TIME',
        experience_min: 1,
        experience_max: 5,
        education_level: 'BACHELOR',
        salary_min: 60000,
        salary_max: 120000,
        deadline: '',
      });
      fetchJobs(companyId);
    } catch (err) {
      setError(formatApiError(err, 'Failed to create job'));
    } finally {
      setCreatingJob(false);
    }
  };

  // Job Status Actions
  const handlePublishJob = async (jobId) => {
    try {
      await jobsAPI.publish(selectedCompanyId, jobId);
      setSuccess('Job published successfully! Candidates can now apply.');
      fetchJobs(selectedCompanyId);
    } catch (err) {
      setError(formatApiError(err, 'Failed to publish job'));
    }
  };

  const handleCloseJob = async (jobId) => {
    try {
      await jobsAPI.close(selectedCompanyId, jobId);
      setSuccess('Job closed to new applications.');
      fetchJobs(selectedCompanyId);
    } catch (err) {
      setError(formatApiError(err, 'Failed to close job'));
    }
  };

  const handleArchiveJob = async (jobId) => {
    try {
      await jobsAPI.archive(selectedCompanyId, jobId);
      setSuccess('Job archived.');
      fetchJobs(selectedCompanyId);
    } catch (err) {
      setError(formatApiError(err, 'Failed to archive job'));
    }
  };

  // View Applicants
  const handleViewApplicants = async (job, status = 'ALL') => {
    setSelectedJobForApplicants(job);
    setLoadingApplicants(true);
    setApplicantStatusFilter(status);
    try {
      const res = await hrApplicationsAPI.getJobApplications(
        job.id,
        selectedCompanyId,
        status === 'ALL' ? undefined : status
      );
      setApplicantsData(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      setError(formatApiError(err, 'Failed to load applicants'));
    } finally {
      setLoadingApplicants(false);
    }
  };

  // Run AI Screening
  const handleRunScreening = async (app) => {
    setScreeningAppId(app.application_id);
    setError('');
    try {
      const res = await screeningAPI.screenApplication(
        app.application_id,
        selectedCompanyId
      );
      const score = Math.round(res.data.match_score || 0);
      const classification = res.data.classification || 'MATCH';
      setSuccess(`AI Screening completed for ${app.candidate_name || 'candidate'}! Score: ${score}% (${classification})`);
      if (selectedJobForApplicants) {
        handleViewApplicants(selectedJobForApplicants, applicantStatusFilter);
      }
      if (detailedApp && detailedApp.application_id === app.application_id) {
        handleViewApplicantDetail(app.application_id);
      }
    } catch (err) {
      setError(formatApiError(err, 'AI screening failed'));
    } finally {
      setScreeningAppId(null);
    }
  };

  // View Applicant Detail
  const handleViewApplicantDetail = async (applicationId) => {
    if (detailedApp && detailedApp.application_id === applicationId) {
      setDetailedApp(null);
      return;
    }
    setLoadingDetail(true);
    try {
      const res = await hrApplicationsAPI.getApplicationDetail(
        applicationId,
        selectedCompanyId
      );
      setDetailedApp(res.data);
    } catch (err) {
      setError(formatApiError(err, 'Failed to load applicant detail'));
    } finally {
      setLoadingDetail(false);
    }
  };

  // Shortlist / Reject
  const handleShortlist = async (applicationId) => {
    try {
      await applicationsAPI.shortlist(applicationId, selectedCompanyId);
      setSuccess('Candidate shortlisted! Email notification sent.');
      if (selectedJobForApplicants) {
        handleViewApplicants(selectedJobForApplicants, applicantStatusFilter);
      }
    } catch (err) {
      setError(formatApiError(err, 'Failed to shortlist candidate'));
    }
  };

  const handleReject = async (applicationId) => {
    try {
      await applicationsAPI.reject(applicationId, selectedCompanyId);
      setSuccess('Candidate application marked as rejected.');
      if (selectedJobForApplicants) {
        handleViewApplicants(selectedJobForApplicants, applicantStatusFilter);
      }
    } catch (err) {
      setError(formatApiError(err, 'Failed to reject candidate'));
    }
  };

  // Schedule Interview
  const handleOpenSchedule = (app) => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(10, 0, 0, 0);
    const startIso = new Date(
      tomorrow.getTime() - tomorrow.getTimezoneOffset() * 60000
    )
      .toISOString()
      .slice(0, 16);
    tomorrow.setHours(11, 0, 0, 0);
    const endIso = new Date(
      tomorrow.getTime() - tomorrow.getTimezoneOffset() * 60000
    )
      .toISOString()
      .slice(0, 16);

    setInterviewForm({
      start_time: startIso,
      end_time: endIso,
      mode: 'ONLINE',
      meeting_url: 'https://meet.google.com/smarthire-interview',
      location: '',
    });
    setSchedulingApp(app);
  };

  const handleScheduleSubmit = async (e) => {
    e.preventDefault();
    if (!schedulingApp) return;

    try {
      setSchedulingLoading(true);
      setError('');
      const payload = {
        application_id: schedulingApp.application_id,
        start_time: new Date(interviewForm.start_time).toISOString(),
        end_time: new Date(interviewForm.end_time).toISOString(),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
        mode: interviewForm.mode,
        meeting_url:
          interviewForm.mode === 'ONLINE' ? interviewForm.meeting_url : null,
        location:
          interviewForm.mode === 'IN_PERSON' ? interviewForm.location : null,
      };

      await interviewsAPI.schedule(payload, selectedCompanyId);
      setSuccess('Interview scheduled! Email invitation sent to the candidate.');
      setSchedulingApp(null);
      if (selectedJobForApplicants) {
        handleViewApplicants(selectedJobForApplicants, applicantStatusFilter);
      }
    } catch (err) {
      setError(formatApiError(err, 'Failed to schedule interview'));
    } finally {
      setSchedulingLoading(false);
    }
  };

  // Job Offer
  const handleOpenOffer = (app) => {
    const today = new Date();
    const startDate = new Date();
    startDate.setDate(today.getDate() + 30);
    const expDate = new Date();
    expDate.setDate(today.getDate() + 14);

    setOfferForm({
      salary: selectedJobForApplicants?.salary_min || 100000,
      currency: 'USD',
      start_date: startDate.toISOString().split('T')[0],
      expiration_date: expDate.toISOString().split('T')[0],
      notes: `Offer for ${selectedJobForApplicants?.title || 'Position'} with full health & 401k benefits.`,
    });
    setOfferModalApp(app);
  };

  const handleSubmitOffer = async (e) => {
    e.preventDefault();
    if (!offerModalApp) return;

    if (offerForm.expiration_date > offerForm.start_date) {
      setError('Offer expiration date must be on or before the start date.');
      return;
    }

    try {
      setCreatingOffer(true);
      setError('');
      await offersAPI.create(selectedCompanyId, {
        application_id: offerModalApp.application_id,
        salary: parseFloat(offerForm.salary),
        currency: offerForm.currency,
        start_date: offerForm.start_date,
        expiration_date: offerForm.expiration_date,
        notes: offerForm.notes || null,
      });
      setSuccess(`Job offer created for ${offerModalApp.candidate_name || 'candidate'}! Check the Offers tab to review and send.`);
      setOfferModalApp(null);
      if (selectedJobForApplicants) {
        handleViewApplicants(selectedJobForApplicants, applicantStatusFilter);
      }
    } catch (err) {
      setError(formatApiError(err, 'Failed to create job offer'));
    } finally {
      setCreatingOffer(false);
    }
  };

  // Direct Hire Decision
  const handleHireDecision = async (applicationId, decision) => {
    if (!window.confirm(`Are you sure you want to mark this candidate decision as ${decision}?`)) {
      return;
    }
    try {
      setLoading(true);
      const res = await hiringAPI.makeDecision(applicationId, decision, selectedCompanyId);
      setSuccess(`Hiring decision recorded: ${res.data.message || decision}`);
      if (selectedJobForApplicants) {
        handleViewApplicants(selectedJobForApplicants, applicantStatusFilter);
      }
    } catch (err) {
      setError(formatApiError(err, 'Failed to record decision'));
    } finally {
      setLoading(false);
    }
  };

  // Candidate Apply
  const handleApply = async (jobId) => {
    setApplyingJobId(jobId);
    setError('');
    setSuccess('');
    try {
      await applicationsAPI.apply(jobId);
      setSuccess('Application submitted! AI resume analysis completed.');
    } catch (err) {
      setError(formatApiError(err, 'Failed to apply. Make sure your primary CV is uploaded.'));
    } finally {
      setApplyingJobId(null);
    }
  };

  const filteredJobs = jobs.filter((j) => {
    const matchesStatus = !isRecruiter || statusFilter === 'ALL' || j.status === statusFilter;
    const matchesSearch =
      !searchQuery ||
      j.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      j.location.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="page-shell">
      {/* Page Header */}
      <div className="page-header-row">
        <div>
          <h1 className="page-title">{isRecruiter ? 'Jobs & Applicant Pipeline' : 'Explore Tech Opportunities'}</h1>
          <p className="page-subtitle">
            {isRecruiter
              ? 'Create positions, inspect AI requirement analyses, and track applicant evaluations.'
              : 'Browse active openings, review match criteria, and apply with 1-click.'}
          </p>
        </div>

        <div className="page-actions-row">
          {isRecruiter && companies.length > 0 && (
            <select
              value={selectedCompanyId}
              onChange={handleCompanyChange}
              className="select-control"
              style={{ width: 'auto', minWidth: '200px' }}
            >
              {companies.map((c) => (
                <option key={c.id} value={c.id}>🏢 {c.name}</option>
              ))}
            </select>
          )}

          {isRecruiter && (
            <Button
              variant="primary"
              size="md"
              icon={Plus}
              onClick={() => setShowCreateModal(true)}
            >
              Post New Job
            </Button>
          )}
        </div>
      </div>

      {/* Alerts */}
      {error && <div className="alert alert-error"><span>⚠️ {error}</span></div>}
      {success && <div className="alert alert-success"><span>✓ {success}</span></div>}

      {/* Search & Filter Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
        <div style={{ width: '320px' }}>
          <Input
            icon={Search}
            placeholder="Search by title or location..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {isRecruiter && (
          <div className="filter-bar" style={{ marginBottom: 0 }}>
            {['ALL', 'PUBLISHED', 'DRAFT', 'CLOSED', 'ARCHIVED'].map((st) => (
              <button
                key={st}
                type="button"
                className={`filter-tab ${statusFilter === st ? 'active' : ''}`}
                onClick={() => setStatusFilter(st)}
              >
                {st === 'ALL' ? 'All Roles' : st}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Jobs Grid */}
      {loading ? (
        <p style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          Loading jobs...
        </p>
      ) : filteredJobs.length === 0 ? (
        <EmptyState
          icon={Briefcase}
          title="No jobs found"
          description={isRecruiter ? 'Create your first job posting to start attracting top talent.' : 'No active jobs matching your criteria.'}
          actionLabel={isRecruiter ? 'Post Job Opening' : undefined}
          onAction={isRecruiter ? () => setShowCreateModal(true) : undefined}
        />
      ) : (
        <div className="card-grid">
          {filteredJobs.map((job) => (
            <Card key={job.id} hover className="job-card-item">
              <Card.Header>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
                  <div>
                    <Card.Title>{job.title}</Card.Title>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px', color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><MapPin size={13} /> {job.location}</span>
                      <span>•</span>
                      <span>{job.employment_type?.replace('_', ' ')}</span>
                    </div>
                  </div>
                  <StatusBadge status={job.status} />
                </div>
              </Card.Header>

              <Card.Content>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineClamp: 3, WebkitLineClamp: 3, display: '-webkit-box', WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {job.description}
                </p>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '16px', paddingTop: '12px', borderTop: '1px solid var(--border-subtle)', fontSize: '0.8125rem' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--text-primary)', fontWeight: 600 }}>
                    <DollarSign size={14} className="text-brand" />
                    ${job.salary_min?.toLocaleString()} – ${job.salary_max?.toLocaleString()}
                  </span>
                  <span style={{ color: 'var(--text-muted)' }}>
                    {job.experience_min}–{job.experience_max} yrs exp
                  </span>
                </div>
              </Card.Content>

              <Card.Footer>
                {isRecruiter ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '100%', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      {job.status === 'DRAFT' && (
                        <Button variant="outline" size="sm" onClick={() => handlePublishJob(job.id)}>
                          Publish
                        </Button>
                      )}
                      {job.status === 'PUBLISHED' && (
                        <Button variant="secondary" size="sm" onClick={() => handleCloseJob(job.id)}>
                          Close
                        </Button>
                      )}
                      {job.status !== 'ARCHIVED' && (
                        <Button variant="ghost" size="sm" onClick={() => handleArchiveJob(job.id)}>
                          Archive
                        </Button>
                      )}
                    </div>
                    <Button
                      variant="primary"
                      size="sm"
                      icon={Users}
                      onClick={() => handleViewApplicants(job)}
                    >
                      Applicants
                    </Button>
                  </div>
                ) : (
                  <Button
                    variant="primary"
                    size="sm"
                    loading={applyingJobId === job.id}
                    onClick={() => handleApply(job.id)}
                    style={{ width: '100%' }}
                  >
                    1-Click AI Apply
                  </Button>
                )}
              </Card.Footer>
            </Card>
          ))}
        </div>
      )}

      {/* Create Job Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Post New Job Opening"
        subtitle="Specify requirements for automated Groq AI candidate screening"
        maxWidth="640px"
      >
        <form onSubmit={handleCreateJob}>
          {error && (
            <div className="alert alert-error" style={{ marginBottom: '16px' }}>
              <span>⚠️ {error}</span>
            </div>
          )}
          <div className="form-grid">
            <div className="form-group full-width">
              <Input
                label="Job Title"
                name="title"
                value={formData.title}
                onChange={handleFormChange}
                placeholder="e.g. Senior Full-Stack Engineer"
                required
              />
            </div>

            <div className="form-group full-width">
              <Textarea
                label="Job Description & Responsibilities"
                name="description"
                value={formData.description}
                onChange={handleFormChange}
                rows={4}
                placeholder="Describe key responsibilities and ideal candidate skills..."
                required
              />
            </div>

            <Input
              label="Location"
              name="location"
              value={formData.location}
              onChange={handleFormChange}
              required
            />

            <Select
              label="Employment Type"
              name="employment_type"
              value={formData.employment_type}
              onChange={handleFormChange}
            >
              <option value="FULL_TIME">Full Time</option>
              <option value="PART_TIME">Part Time</option>
              <option value="CONTRACT">Contract</option>
              <option value="INTERNSHIP">Internship</option>
            </Select>

            <Input
              label="Min Experience (Yrs)"
              name="experience_min"
              type="number"
              value={formData.experience_min}
              onChange={handleFormChange}
            />

            <Input
              label="Max Experience (Yrs)"
              name="experience_max"
              type="number"
              value={formData.experience_max}
              onChange={handleFormChange}
            />

            <Input
              label="Min Salary ($)"
              name="salary_min"
              type="number"
              value={formData.salary_min}
              onChange={handleFormChange}
            />

            <Input
              label="Max Salary ($)"
              name="salary_max"
              type="number"
              value={formData.salary_max}
              onChange={handleFormChange}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' }}>
            <Button variant="secondary" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={creatingJob}>
              Create & Analyze Job
            </Button>
          </div>
        </form>
      </Modal>

      {/* Applicants Drawer */}
      <Drawer
        isOpen={Boolean(selectedJobForApplicants)}
        onClose={() => {
          setSelectedJobForApplicants(null);
          setDetailedApp(null);
        }}
        title={`Applicants: ${selectedJobForApplicants?.title || 'Job'}`}
        subtitle="Screen candidates with Groq AI, shortlist, schedule interviews, and make offers"
        width="680px"
      >
        <div style={{ marginBottom: '16px' }}>
          <div className="filter-bar" style={{ width: '100%', overflowX: 'auto' }}>
            {['ALL', 'APPLIED', 'SHORTLISTED', 'INTERVIEWING', 'OFFERED', 'HIRED', 'REJECTED'].map((st) => (
              <button
                key={st}
                type="button"
                className={`filter-tab ${applicantStatusFilter === st ? 'active' : ''}`}
                onClick={() => handleViewApplicants(selectedJobForApplicants, st)}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        {loadingApplicants ? (
          <p style={{ textAlign: 'center', padding: '32px' }}>Loading applicant records...</p>
        ) : applicantsData.length === 0 ? (
          <EmptyState
            icon={Users}
            title="No applicants found"
            description="No candidates have applied to this role in the selected status."
          />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {applicantsData.map((app) => (
              <Card key={app.application_id} style={{ padding: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <ScoreCircle score={app.match_score || 0} size={56} strokeWidth={5} />
                    <div>
                      <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>
                        {app.candidate_name || app.email || 'Candidate'}
                      </h4>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                        <StatusBadge status={app.status} />
                        {app.classification && <StatusBadge status={app.classification} />}
                      </div>
                    </div>
                  </div>

                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {app.applied_at ? new Date(app.applied_at).toLocaleDateString() : ''}
                  </span>
                </div>

                {/* Detailed AI Card if loaded */}
                {detailedApp && detailedApp.application_id === app.application_id && (
                  <AIScreeningCard screeningResult={detailedApp.screening || detailedApp} />
                )}

                {/* Candidate Action Buttons */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '8px', marginTop: '16px', paddingTop: '12px', borderTop: '1px solid var(--border-subtle)', flexWrap: 'wrap' }}>
                  <Button
                    variant="ghost"
                    size="sm"
                    loading={loadingDetail}
                    onClick={() => handleViewApplicantDetail(app.application_id)}
                  >
                    {detailedApp && detailedApp.application_id === app.application_id ? 'Hide Details' : 'View AI Breakdown'}
                  </Button>

                  <Button
                    variant="ai"
                    size="sm"
                    icon={Sparkles}
                    loading={screeningAppId === app.application_id}
                    onClick={() => handleRunScreening(app)}
                  >
                    Run AI Screening
                  </Button>

                  {app.status === 'APPLIED' && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleShortlist(app.application_id)}
                    >
                      Shortlist
                    </Button>
                  )}

                  {['SHORTLISTED', 'INTERVIEWING'].includes(app.status) && (
                    <Button
                      variant="secondary"
                      size="sm"
                      icon={Calendar}
                      onClick={() => handleOpenSchedule(app)}
                    >
                      Schedule Interview
                    </Button>
                  )}

                  {['SHORTLISTED', 'INTERVIEWING'].includes(app.status) && (
                    <Button
                      variant="primary"
                      size="sm"
                      icon={Award}
                      onClick={() => handleOpenOffer(app)}
                    >
                      Make Offer
                    </Button>
                  )}

                  {app.status === 'INTERVIEWING' && (
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleHireDecision(app.application_id, 'HIRE')}
                    >
                      Hire
                    </Button>
                  )}

                  {app.status !== 'REJECTED' && (
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleReject(app.application_id)}
                    >
                      Reject
                    </Button>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </Drawer>

      {/* Schedule Interview Modal */}
      <Modal
        isOpen={Boolean(schedulingApp)}
        onClose={() => setSchedulingApp(null)}
        title={`Schedule Interview: ${schedulingApp?.candidate_name || 'Candidate'}`}
        subtitle="Sets interview mode, calendar time slot, and sends calendar invitation"
        maxWidth="520px"
      >
        <form onSubmit={handleScheduleSubmit}>
          <div className="form-grid">
            <Input
              label="Start Date & Time"
              type="datetime-local"
              value={interviewForm.start_time}
              onChange={(e) => setInterviewForm({ ...interviewForm, start_time: e.target.value })}
              required
            />
            <Input
              label="End Date & Time"
              type="datetime-local"
              value={interviewForm.end_time}
              onChange={(e) => setInterviewForm({ ...interviewForm, end_time: e.target.value })}
              required
            />
            <Select
              label="Interview Mode"
              value={interviewForm.mode}
              onChange={(e) => setInterviewForm({ ...interviewForm, mode: e.target.value })}
            >
              <option value="ONLINE">Online (Video Meet)</option>
              <option value="IN_PERSON">In-Person</option>
              <option value="PHONE">Phone Call</option>
            </Select>

            {interviewForm.mode === 'ONLINE' ? (
              <Input
                label="Meeting Video URL"
                value={interviewForm.meeting_url}
                onChange={(e) => setInterviewForm({ ...interviewForm, meeting_url: e.target.value })}
                required
              />
            ) : (
              <Input
                label="Office / Physical Location"
                value={interviewForm.location}
                onChange={(e) => setInterviewForm({ ...interviewForm, location: e.target.value })}
                placeholder="e.g. 100 Main St, Room 4B"
                required
              />
            )}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' }}>
            <Button variant="secondary" onClick={() => setSchedulingApp(null)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={schedulingLoading}>
              Confirm & Send Invite
            </Button>
          </div>
        </form>
      </Modal>

      {/* Make Offer Modal */}
      <Modal
        isOpen={Boolean(offerModalApp)}
        onClose={() => setOfferModalApp(null)}
        title={`Extend Job Offer: ${offerModalApp?.candidate_name || 'Candidate'}`}
        subtitle="Formulates formal compensation package and sends offer letter"
        maxWidth="540px"
      >
        <form onSubmit={handleSubmitOffer}>
          <div className="form-grid">
            <Input
              label="Annual Salary ($)"
              type="number"
              value={offerForm.salary}
              onChange={(e) => setOfferForm({ ...offerForm, salary: e.target.value })}
              required
            />
            <Select
              label="Currency"
              value={offerForm.currency}
              onChange={(e) => setOfferForm({ ...offerForm, currency: e.target.value })}
            >
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
            </Select>
            <Input
              label="Proposed Start Date"
              type="date"
              value={offerForm.start_date}
              onChange={(e) => setOfferForm({ ...offerForm, start_date: e.target.value })}
              required
            />
            <Input
              label="Offer Expiration Date"
              type="date"
              value={offerForm.expiration_date}
              onChange={(e) => setOfferForm({ ...offerForm, expiration_date: e.target.value })}
              required
            />
            <div className="form-group full-width">
              <Textarea
                label="Offer Notes & Terms"
                value={offerForm.notes}
                onChange={(e) => setOfferForm({ ...offerForm, notes: e.target.value })}
                rows={3}
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' }}>
            <Button variant="secondary" onClick={() => setOfferModalApp(null)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={creatingOffer}>
              Generate & Record Offer
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
