import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { companiesAPI, interviewsAPI, formatApiError } from '../services/api';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import StatusBadge from '../components/ui/StatusBadge';
import Modal from '../components/ui/Modal';
import EmptyState from '../components/ui/EmptyState';
import { Input, Select, Textarea } from '../components/ui/Input';
import {
  Calendar,
  Clock,
  Video,
  MapPin,
  CheckCircle2,
  FileText,
  ExternalLink,
  Copy,
  Check,
} from 'lucide-react';
import './Page.css';

export default function Interviews() {
  const { user } = useAuth();
  const isRecruiter = ['OWNER', 'HR', 'RECRUITER', 'COMPANY_ADMIN'].includes(
    user?.role?.toUpperCase()
  );

  const [interviews, setInterviews] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState('');
  const [loading, setLoading] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [copiedId, setCopiedId] = useState(null);

  // Feedback Modal State
  const [feedbackInterview, setFeedbackInterview] = useState(null);
  const [feedbackForm, setFeedbackForm] = useState({
    rating: 8.5,
    technical_score: 8.0,
    communication_score: 8.5,
    culture_score: 9.0,
    comments: '',
    recommendation: 'HIRE',
  });
  const [submittingFeedback, setSubmittingFeedback] = useState(false);

  const fetchInterviews = useCallback(
    async (companyId) => {
      try {
        setLoading(true);
        setError('');
        if (!isRecruiter) {
          const res = await interviewsAPI.getMyInterviews();
          const list = Array.isArray(res.data)
            ? res.data
            : res.data?.interviews || [];
          setInterviews(list);
        } else {
          const cId = companyId || selectedCompanyId;
          if (!cId) {
            setInterviews([]);
            return;
          }
          const res = await interviewsAPI.listCompanyInterviews(cId);
          const list = Array.isArray(res.data) ? res.data : [];
          setInterviews(list);
        }
      } catch (err) {
        setError(formatApiError(err, 'Failed to load interviews'));
      } finally {
        setLoading(false);
      }
    },
    [isRecruiter, selectedCompanyId]
  );

  const fetchCompanies = useCallback(async () => {
    if (!isRecruiter) return;
    try {
      const res = await companiesAPI.list();
      const data = res.data || [];
      setCompanies(data);
      if (data.length > 0) {
        setSelectedCompanyId(data[0].id);
        fetchInterviews(data[0].id);
      }
    } catch (err) {
      // Handled
    }
  }, [isRecruiter, fetchInterviews]);

  useEffect(() => {
    if (isRecruiter) {
      fetchCompanies();
    } else {
      fetchInterviews();
    }
  }, [isRecruiter, fetchCompanies, fetchInterviews]);

  const handleCompanyChange = (e) => {
    const newCompanyId = e.target.value;
    setSelectedCompanyId(newCompanyId);
    fetchInterviews(newCompanyId);
  };

  // Candidate Confirm Interview
  const handleConfirmInterview = async (interviewId) => {
    try {
      setActionLoadingId(interviewId);
      setError('');
      await interviewsAPI.confirm(interviewId);
      setSuccess('Interview attendance confirmed! The recruiter has been notified.');
      fetchInterviews();
    } catch (err) {
      setError(formatApiError(err, 'Failed to confirm interview'));
    } finally {
      setActionLoadingId(null);
    }
  };

  // Recruiter Cancel Interview
  const handleCancelInterview = async (interviewId) => {
    if (!window.confirm('Are you sure you want to cancel this interview?')) {
      return;
    }
    try {
      setActionLoadingId(interviewId);
      setError('');
      await interviewsAPI.cancel(interviewId, selectedCompanyId);
      setSuccess('Interview has been cancelled.');
      fetchInterviews();
    } catch (err) {
      setError(formatApiError(err, 'Failed to cancel interview'));
    } finally {
      setActionLoadingId(null);
    }
  };

  // Recruiter Complete Interview
  const handleCompleteInterview = async (interviewId) => {
    try {
      setActionLoadingId(interviewId);
      setError('');
      await interviewsAPI.complete(interviewId, selectedCompanyId);
      setSuccess('Interview marked as completed! You can now record evaluation feedback.');
      fetchInterviews();
    } catch (err) {
      setError(formatApiError(err, 'Failed to complete interview'));
    } finally {
      setActionLoadingId(null);
    }
  };

  // Recruiter Mark No-Show
  const handleNoShowInterview = async (interviewId) => {
    if (!window.confirm('Mark candidate as No-Show for this interview?')) {
      return;
    }
    try {
      setActionLoadingId(interviewId);
      setError('');
      await interviewsAPI.noShow(interviewId, selectedCompanyId);
      setSuccess('Interview marked as No-Show.');
      fetchInterviews();
    } catch (err) {
      setError(formatApiError(err, 'Failed to record no-show'));
    } finally {
      setActionLoadingId(null);
    }
  };

  // Submit Feedback
  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    if (!feedbackInterview) return;
    try {
      setSubmittingFeedback(true);
      setError('');
      await interviewsAPI.feedback(
        feedbackInterview.id,
        {
          rating: parseFloat(feedbackForm.rating),
          technical_score: parseFloat(feedbackForm.technical_score),
          communication_score: parseFloat(feedbackForm.communication_score),
          culture_score: parseFloat(feedbackForm.culture_score),
          comments: feedbackForm.comments || null,
          recommendation: feedbackForm.recommendation,
        },
        selectedCompanyId
      );
      setSuccess(`Interview evaluation recorded! Recommendation: ${feedbackForm.recommendation}`);
      setFeedbackInterview(null);
      fetchInterviews();
    } catch (err) {
      setError(formatApiError(err, 'Failed to submit interview feedback'));
    } finally {
      setSubmittingFeedback(false);
    }
  };

  const handleCopyMeetingUrl = (url, id) => {
    navigator.clipboard.writeText(url);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filteredInterviews = interviews.filter((i) => {
    if (statusFilter === 'ALL') return true;
    return i.status === statusFilter;
  });

  return (
    <div className="page-shell">
      {/* Header */}
      <div className="page-header-row">
        <div>
          <h1 className="page-title">Interview Schedules & Reviews</h1>
          <p className="page-subtitle">
            {isRecruiter
              ? 'Orchestrate interviews, join video meetings, and record structured evaluation feedback.'
              : 'View upcoming interviews, access video meeting rooms, and confirm attendance.'}
          </p>
        </div>

        <div className="page-actions-row">
          {isRecruiter && companies.length > 0 && (
            <select
              value={selectedCompanyId}
              onChange={handleCompanyChange}
              className="select-control"
              style={{ width: 'auto', minWidth: '180px' }}
            >
              {companies.map((c) => (
                <option key={c.id} value={c.id}>
                  🏢 {c.name}
                </option>
              ))}
            </select>
          )}

          <div className="filter-bar" style={{ marginBottom: 0 }}>
            {['ALL', 'SCHEDULED', 'CONFIRMED', 'COMPLETED', 'NO_SHOW', 'CANCELLED'].map((st) => (
              <button
                key={st}
                type="button"
                className={`filter-tab ${statusFilter === st ? 'active' : ''}`}
                onClick={() => setStatusFilter(st)}
              >
                {st === 'ALL' ? 'All' : st}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && <div className="alert alert-error"><span>⚠️ {error}</span></div>}
      {success && <div className="alert alert-success"><span>✓ {success}</span></div>}

      {/* Interview Cards List */}
      {loading ? (
        <p style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          Loading interview schedules...
        </p>
      ) : filteredInterviews.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title="No interviews found"
          description={
            isRecruiter
              ? 'Schedule interviews from the Jobs & Applicant Pipeline tab to see them here.'
              : 'No scheduled interviews at this time.'
          }
        />
      ) : (
        <div className="card-grid">
          {filteredInterviews.map((item) => {
            const startDate = item.start_time ? new Date(item.start_time) : null;
            const endDate = item.end_time ? new Date(item.end_time) : null;

            return (
              <Card key={item.id} hover>
                <Card.Header>
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
                    <div>
                      <Card.Title>
                        {item.job_title || item.application?.job?.title || 'Technical Interview'}
                      </Card.Title>
                      <Card.Description>
                        Candidate: {item.candidate_name || item.candidate?.user?.first_name || 'Assigned Candidate'}
                      </Card.Description>
                    </div>
                    <StatusBadge status={item.status} />
                  </div>
                </Card.Header>

                <Card.Content>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.875rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
                      <Calendar size={15} className="text-brand" />
                      <span>{startDate ? startDate.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }) : 'TBD'}</span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
                      <Clock size={15} className="text-brand" />
                      <span>
                        {startDate ? startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''} –{' '}
                        {endDate ? endDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                      </span>
                    </div>

                    {item.mode === 'ONLINE' && item.meeting_url && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                        <Video size={15} style={{ color: 'var(--brand-500)' }} />
                        <a
                          href={item.meeting_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ fontSize: '0.8125rem', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                        >
                          Open Video Room <ExternalLink size={12} />
                        </a>
                        <button
                          type="button"
                          onClick={() => handleCopyMeetingUrl(item.meeting_url, item.id)}
                          style={{ color: 'var(--text-muted)', marginLeft: '6px' }}
                          title="Copy meeting link"
                        >
                          {copiedId === item.id ? <Check size={14} style={{ color: 'var(--success-500)' }} /> : <Copy size={14} />}
                        </button>
                      </div>
                    )}

                    {item.mode === 'IN_PERSON' && item.location && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
                        <MapPin size={15} />
                        <span>{item.location}</span>
                      </div>
                    )}
                  </div>
                </Card.Content>

                <Card.Footer>
                  {!isRecruiter ? (
                    item.status === 'SCHEDULED' ? (
                      <Button
                        variant="primary"
                        size="sm"
                        icon={CheckCircle2}
                        loading={actionLoadingId === item.id}
                        onClick={() => handleConfirmInterview(item.id)}
                        style={{ width: '100%' }}
                      >
                        Confirm Attendance ✓
                      </Button>
                    ) : (
                      <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                        {item.status === 'CONFIRMED' ? '✓ Attendance Confirmed' : item.status}
                      </span>
                    )
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', gap: '6px', flexWrap: 'wrap' }}>
                      <div style={{ display: 'flex', gap: '6px' }}>
                        {['SCHEDULED', 'CONFIRMED'].includes(item.status) && (
                          <Button
                            variant="secondary"
                            size="sm"
                            loading={actionLoadingId === item.id}
                            onClick={() => handleCompleteInterview(item.id)}
                          >
                            Complete
                          </Button>
                        )}
                        {['SCHEDULED', 'CONFIRMED'].includes(item.status) && (
                          <Button
                            variant="outline"
                            size="sm"
                            loading={actionLoadingId === item.id}
                            onClick={() => handleNoShowInterview(item.id)}
                          >
                            No-Show
                          </Button>
                        )}
                        {item.status !== 'CANCELLED' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            loading={actionLoadingId === item.id}
                            onClick={() => handleCancelInterview(item.id)}
                          >
                            Cancel
                          </Button>
                        )}
                      </div>

                      {item.status === 'COMPLETED' && (
                        <Button
                          variant="ai"
                          size="sm"
                          icon={FileText}
                          onClick={() => {
                            setFeedbackInterview(item);
                            setFeedbackForm({
                              rating: 8.5,
                              technical_score: 8.0,
                              communication_score: 8.5,
                              culture_score: 9.0,
                              comments: '',
                              recommendation: 'HIRE',
                            });
                          }}
                        >
                          Submit Feedback
                        </Button>
                      )}
                    </div>
                  )}
                </Card.Footer>
              </Card>
            );
          })}
        </div>
      )}

      {/* Feedback Evaluation Modal */}
      <Modal
        isOpen={Boolean(feedbackInterview)}
        onClose={() => setFeedbackInterview(null)}
        title="Candidate Interview Evaluation"
        subtitle="Submit structured assessment scores and recommendation"
        maxWidth="520px"
      >
        <form onSubmit={handleSubmitFeedback}>
          <div className="form-grid">
            <Input
              label="Overall Rating (0 - 10)"
              type="number"
              step="0.1"
              min="0"
              max="10"
              value={feedbackForm.rating}
              onChange={(e) => setFeedbackForm({ ...feedbackForm, rating: e.target.value })}
              required
            />
            <Input
              label="Technical Proficiency (0 - 10)"
              type="number"
              step="0.1"
              min="0"
              max="10"
              value={feedbackForm.technical_score}
              onChange={(e) => setFeedbackForm({ ...feedbackForm, technical_score: e.target.value })}
              required
            />
            <Input
              label="Communication & Articulation"
              type="number"
              step="0.1"
              min="0"
              max="10"
              value={feedbackForm.communication_score}
              onChange={(e) => setFeedbackForm({ ...feedbackForm, communication_score: e.target.value })}
              required
            />
            <Input
              label="Culture & Team Alignment"
              type="number"
              step="0.1"
              min="0"
              max="10"
              value={feedbackForm.culture_score}
              onChange={(e) => setFeedbackForm({ ...feedbackForm, culture_score: e.target.value })}
              required
            />
            <div className="form-group full-width">
              <Select
                label="Hiring Recommendation"
                value={feedbackForm.recommendation}
                onChange={(e) => setFeedbackForm({ ...feedbackForm, recommendation: e.target.value })}
              >
                <option value="STRONG_HIRE">🌟 Strong Hire</option>
                <option value="HIRE">👍 Hire</option>
                <option value="NO_HIRE">⚠️ No Hire</option>
                <option value="STRONG_NO_HIRE">⛔ Strong No Hire</option>
              </Select>
            </div>
            <div className="form-group full-width">
              <Textarea
                label="Interviewer Notes & Rationale"
                value={feedbackForm.comments}
                onChange={(e) => setFeedbackForm({ ...feedbackForm, comments: e.target.value })}
                placeholder="Key strengths demonstrated, areas of hesitation, project depth..."
                rows={4}
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' }}>
            <Button variant="secondary" onClick={() => setFeedbackInterview(null)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={submittingFeedback}>
              Record Evaluation
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
