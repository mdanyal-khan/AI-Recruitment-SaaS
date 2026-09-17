import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { offersAPI, candidateOffersAPI, companiesAPI, formatApiError } from '../services/api';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import StatusBadge from '../components/ui/StatusBadge';
import Modal from '../components/ui/Modal';
import EmptyState from '../components/ui/EmptyState';
import {
  Award,
  CheckCircle2,
  Send,
} from 'lucide-react';
import './Page.css';

export default function Offers() {
  const { user } = useAuth();
  const isRecruiter = ['OWNER', 'HR', 'RECRUITER', 'COMPANY_ADMIN'].includes(
    user?.role?.toUpperCase()
  );

  const [offers, setOffers] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState('');
  const [loading, setLoading] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Candidate confirmation modal
  const [confirmAcceptOffer, setConfirmAcceptOffer] = useState(null);
  const [confirmDeclineOffer, setConfirmDeclineOffer] = useState(null);

  // Fetch candidate offers
  const fetchCandidateOffers = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const res = await candidateOffersAPI.list();
      const list = Array.isArray(res.data) ? res.data : [];
      setOffers(list);
    } catch (err) {
      setError(formatApiError(err, 'Failed to load your job offers'));
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch company offers for HR
  const fetchCompanyOffers = useCallback(async (companyId) => {
    if (!companyId) return;
    try {
      setLoading(true);
      setError('');
      const res = await offersAPI.list(companyId);
      const list = Array.isArray(res.data) ? res.data : [];
      setOffers(list);
    } catch (err) {
      setError(formatApiError(err, 'Failed to load company offers'));
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch companies for HR selector
  const fetchCompanies = useCallback(async () => {
    if (!isRecruiter) return;
    try {
      const res = await companiesAPI.list();
      const data = res.data || [];
      setCompanies(data);
      if (data.length > 0) {
        setSelectedCompanyId(data[0].id);
        fetchCompanyOffers(data[0].id);
      }
    } catch (err) {
      // Handled
    }
  }, [isRecruiter, fetchCompanyOffers]);

  useEffect(() => {
    if (isRecruiter) {
      fetchCompanies();
    } else {
      fetchCandidateOffers();
    }
  }, [isRecruiter, fetchCompanies, fetchCandidateOffers]);

  const handleCompanyChange = (e) => {
    const newId = e.target.value;
    setSelectedCompanyId(newId);
    fetchCompanyOffers(newId);
  };

  // Candidate Accept Offer
  const handleAcceptOffer = async (offerId) => {
    try {
      setActionLoadingId(offerId);
      setError('');
      await candidateOffersAPI.accept(offerId);
      setSuccess('🎉 Congratulations! You have accepted the job offer. Your hiring status is now HIRED!');
      setConfirmAcceptOffer(null);
      fetchCandidateOffers();
    } catch (err) {
      setError(formatApiError(err, 'Failed to accept offer'));
    } finally {
      setActionLoadingId(null);
    }
  };

  // Candidate Decline Offer
  const handleDeclineOffer = async (offerId) => {
    try {
      setActionLoadingId(offerId);
      setError('');
      await candidateOffersAPI.decline(offerId);
      setSuccess('Job offer has been declined.');
      setConfirmDeclineOffer(null);
      fetchCandidateOffers();
    } catch (err) {
      setError(formatApiError(err, 'Failed to decline offer'));
    } finally {
      setActionLoadingId(null);
    }
  };

  // HR Actions: Send Offer
  const handleSendOffer = async (offerId) => {
    try {
      setActionLoadingId(offerId);
      setError('');
      await offersAPI.updateStatus(offerId, 'SENT', selectedCompanyId);
      setSuccess('✓ Offer officially sent to the candidate! Candidate notification dispatched.');
      fetchCompanyOffers(selectedCompanyId);
    } catch (err) {
      setError(formatApiError(err, 'Failed to send offer'));
    } finally {
      setActionLoadingId(null);
    }
  };

  // HR Actions: Cancel Offer
  const handleCancelOffer = async (offerId) => {
    if (!window.confirm('Are you sure you want to cancel this job offer?')) {
      return;
    }
    try {
      setActionLoadingId(offerId);
      setError('');
      await offersAPI.updateStatus(offerId, 'CANCELLED', selectedCompanyId);
      setSuccess('Offer has been cancelled.');
      fetchCompanyOffers(selectedCompanyId);
    } catch (err) {
      setError(formatApiError(err, 'Failed to cancel offer'));
    } finally {
      setActionLoadingId(null);
    }
  };

  const filteredOffers = offers.filter((o) => {
    if (statusFilter === 'ALL') return true;
    return o.status === statusFilter;
  });

  return (
    <div className="page-shell">
      {/* Header */}
      <div className="page-header-row">
        <div>
          <h1 className="page-title">{isRecruiter ? 'Offers & Final Hires Pipeline' : 'My Job Offers'}</h1>
          <p className="page-subtitle">
            {isRecruiter
              ? 'Extend formal compensation proposals, track candidate acceptances, and finalize employment.'
              : 'Review received employment offers, evaluate compensation packages, and accept or decline.'}
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
            {['ALL', 'PENDING', 'SENT', 'ACCEPTED', 'DECLINED', 'CANCELLED'].map((st) => (
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

      {/* Offers Cards */}
      {loading ? (
        <p style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          Loading compensation offers...
        </p>
      ) : filteredOffers.length === 0 ? (
        <EmptyState
          icon={Award}
          title="No offers found"
          description={
            isRecruiter
              ? 'Generate job offers for shortlisted or interviewed candidates from the Jobs tab.'
              : 'You do not have any job offers matching this status.'
          }
        />
      ) : (
        <div className="card-grid">
          {filteredOffers.map((offer) => {
            const isAccepted = offer.status === 'ACCEPTED';
            const isSent = offer.status === 'SENT';

            return (
              <Card key={offer.id} hover className={isAccepted ? 'card-hired-glow' : ''}>
                <Card.Header>
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
                    <div>
                      <Card.Title>
                        {offer.job_title || offer.application?.job?.title || 'Employment Proposal'}
                      </Card.Title>
                      <Card.Description>
                        {isRecruiter
                          ? `Candidate: ${offer.candidate_name || offer.candidate?.user?.first_name || 'Candidate'}`
                          : `Company: ${offer.company_name || 'Hiring Organization'}`}
                      </Card.Description>
                    </div>
                    <StatusBadge status={offer.status} />
                  </div>
                </Card.Header>

                <Card.Content>
                  {/* Compensation Highlighting */}
                  <div style={{ padding: '16px', backgroundColor: 'var(--bg-surface-subtle)', borderRadius: 'var(--radius-md)', marginBottom: '16px' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 600 }}>
                      Proposed Annual Compensation
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--brand-600)', marginTop: '2px' }}>
                      ${Number(offer.salary || 0).toLocaleString()} {offer.currency || 'USD'}
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.8125rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Proposed Start Date</span>
                      <span style={{ fontWeight: 600 }}>{offer.start_date ? new Date(offer.start_date).toLocaleDateString() : 'Immediate'}</span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Offer Expiration</span>
                      <span style={{ fontWeight: 600, color: 'var(--warning-600)' }}>
                        {offer.expiration_date ? new Date(offer.expiration_date).toLocaleDateString() : 'N/A'}
                      </span>
                    </div>

                    {offer.notes && (
                      <div style={{ marginTop: '8px', padding: '10px', backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', color: 'var(--text-secondary)', fontSize: '0.8125rem' }}>
                        "{offer.notes}"
                      </div>
                    )}
                  </div>
                </Card.Content>

                <Card.Footer>
                  {!isRecruiter ? (
                    isSent ? (
                      <div style={{ display: 'flex', gap: '8px', width: '100%', justifyContent: 'flex-end' }}>
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => setConfirmDeclineOffer(offer)}
                        >
                          Decline
                        </Button>
                        <Button
                          variant="primary"
                          size="sm"
                          icon={CheckCircle2}
                          onClick={() => setConfirmAcceptOffer(offer)}
                        >
                          Accept Offer ✓
                        </Button>
                      </div>
                    ) : isAccepted ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--success-600)', fontWeight: 600, fontSize: '0.875rem' }}>
                        <CheckCircle2 size={16} />
                        <span>Accepted! You are hired for this position.</span>
                      </div>
                    ) : (
                      <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Status: {offer.status}</span>
                    )
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        {offer.status === 'PENDING' && (
                          <Button
                            variant="primary"
                            size="sm"
                            icon={Send}
                            loading={actionLoadingId === offer.id}
                            onClick={() => handleSendOffer(offer.id)}
                          >
                            Send to Candidate
                          </Button>
                        )}
                        {['PENDING', 'SENT'].includes(offer.status) && (
                          <Button
                            variant="ghost"
                            size="sm"
                            loading={actionLoadingId === offer.id}
                            onClick={() => handleCancelOffer(offer.id)}
                          >
                            Cancel
                          </Button>
                        )}
                      </div>

                      {isAccepted && (
                        <span style={{ color: 'var(--success-600)', fontSize: '0.8125rem', fontWeight: 600 }}>
                          🎉 Candidate Hired
                        </span>
                      )}
                    </div>
                  )}
                </Card.Footer>
              </Card>
            );
          })}
        </div>
      )}

      {/* Confirmation Modal: Accept Offer */}
      <Modal
        isOpen={Boolean(confirmAcceptOffer)}
        onClose={() => setConfirmAcceptOffer(null)}
        title="Accept Employment Offer"
        subtitle="Confirming your new career milestone"
        maxWidth="460px"
      >
        <p style={{ fontSize: '0.9375rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          You are about to accept the offer for <strong>{confirmAcceptOffer?.job_title || 'this position'}</strong> with an annual salary of{' '}
          <strong>${Number(confirmAcceptOffer?.salary || 0).toLocaleString()} {confirmAcceptOffer?.currency}</strong>.
        </p>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '8px' }}>
          This will update your application status to <strong>HIRED</strong> and alert the recruitment team.
        </p>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
          <Button variant="secondary" onClick={() => setConfirmAcceptOffer(null)}>
            Review Further
          </Button>
          <Button
            variant="primary"
            icon={CheckCircle2}
            loading={actionLoadingId === confirmAcceptOffer?.id}
            onClick={() => handleAcceptOffer(confirmAcceptOffer.id)}
          >
            Confirm & Accept Offer
          </Button>
        </div>
      </Modal>

      {/* Confirmation Modal: Decline Offer */}
      <Modal
        isOpen={Boolean(confirmDeclineOffer)}
        onClose={() => setConfirmDeclineOffer(null)}
        title="Decline Employment Offer"
        subtitle="Please confirm if you want to decline"
        maxWidth="460px"
      >
        <p style={{ fontSize: '0.9375rem', color: 'var(--text-secondary)' }}>
          Are you sure you wish to decline the offer for <strong>{confirmDeclineOffer?.job_title}</strong>? This decision cannot be reversed.
        </p>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
          <Button variant="secondary" onClick={() => setConfirmDeclineOffer(null)}>
            Keep Active
          </Button>
          <Button
            variant="danger"
            loading={actionLoadingId === confirmDeclineOffer?.id}
            onClick={() => handleDeclineOffer(confirmDeclineOffer.id)}
          >
            Decline Offer
          </Button>
        </div>
      </Modal>
    </div>
  );
}
