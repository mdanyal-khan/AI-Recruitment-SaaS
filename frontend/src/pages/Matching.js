import React, { useState, useEffect, useCallback } from 'react';
import { companiesAPI, jobsAPI, matchingAPI, candidatesAPI, hrApplicationsAPI, formatApiError } from '../services/api';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import StatusBadge from '../components/ui/StatusBadge';
import { ScoreCircle, ScoreBar } from '../components/ui/ScoreIndicator';
import EmptyState from '../components/ui/EmptyState';
import {
  Sparkles,
  CheckCircle2,
  AlertCircle,
  ShieldAlert,
} from 'lucide-react';
import './Page.css';
import './Matching.css';

export default function Matching() {
  const [companies, setCompanies] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [applicants, setApplicants] = useState([]);
  const [loadingApplicants, setLoadingApplicants] = useState(false);
  const [customUuidMode, setCustomUuidMode] = useState(false);
  const [myCandidateId, setMyCandidateId] = useState('');
  const [selectedCompanyId, setSelectedCompanyId] = useState('');
  const [selectedJobId, setSelectedJobId] = useState('');
  const [candidateId, setCandidateId] = useState('');
  const [loading, setLoading] = useState(false);
  const [matching, setMatching] = useState(false);
  const [error, setError] = useState('');
  const [matchResult, setMatchResult] = useState(null);

  useEffect(() => {
    const initData = async () => {
      try {
        setLoading(true);
        const [compRes, candRes] = await Promise.allSettled([
          companiesAPI.list(),
          candidatesAPI.getProfile(),
        ]);

        if (compRes.status === 'fulfilled' && compRes.value.data?.length > 0) {
          setCompanies(compRes.value.data);
          setSelectedCompanyId(compRes.value.data[0].id);
        }

        if (candRes.status === 'fulfilled' && candRes.value.data?.id) {
          setMyCandidateId(candRes.value.data.id);
          setCandidateId(candRes.value.data.id);
        }
      } catch (err) {
        setError('Failed to load companies or candidate profile');
      } finally {
        setLoading(false);
      }
    };
    initData();
  }, []);

  const fetchJobs = useCallback(async (companyId) => {
    if (!companyId) return;
    try {
      const response = await jobsAPI.list(companyId);
      const list = response.data || [];
      setJobs(list);
      if (list.length > 0) {
        setSelectedJobId(list[0].id);
      } else {
        setSelectedJobId('');
      }
    } catch (err) {
      setJobs([]);
    }
  }, []);

  const fetchApplicants = useCallback(async (jobId, companyId) => {
    if (!jobId || !companyId) {
      setApplicants([]);
      return;
    }
    try {
      setLoadingApplicants(true);
      const res = await hrApplicationsAPI.getJobApplications(jobId, companyId);
      const list = Array.isArray(res.data) ? res.data : [];
      setApplicants(list);
      if (list.length > 0) {
        setCandidateId(list[0].candidate_id);
      }
    } catch (err) {
      setApplicants([]);
    } finally {
      setLoadingApplicants(false);
    }
  }, []);

  useEffect(() => {
    if (selectedCompanyId) {
      fetchJobs(selectedCompanyId);
    }
  }, [selectedCompanyId, fetchJobs]);

  useEffect(() => {
    if (selectedJobId && selectedCompanyId) {
      fetchApplicants(selectedJobId, selectedCompanyId);
    } else {
      setApplicants([]);
    }
  }, [selectedJobId, selectedCompanyId, fetchApplicants]);

  const handleCompanyChange = (e) => {
    setSelectedCompanyId(e.target.value);
    setMatchResult(null);
    setError('');
  };

  const handleMatch = async () => {
    if (!selectedJobId) {
      setError('Please select a job opening to evaluate.');
      return;
    }
    if (!candidateId.trim()) {
      setError('Please enter or select a valid candidate ID.');
      return;
    }

    try {
      setMatching(true);
      setError('');
      setMatchResult(null);

      const response = await matchingAPI.matchCandidate(
        selectedJobId,
        candidateId.trim(),
        selectedCompanyId
      );
      setMatchResult(response.data);
    } catch (err) {
      setError(
        formatApiError(
          err,
          'Matching analysis failed. Ensure the candidate has an uploaded and analyzed resume.'
        )
      );
    } finally {
      setMatching(false);
    }
  };

  const explanation = matchResult?.explanation || {};
  const matchedSkills = explanation.matched_skills || [];
  const missingSkills = matchResult?.missing_skills || [];
  const strengths = explanation.strengths || [];
  const weaknesses = explanation.weaknesses || [];

  return (
    <div className="page-shell">
      {/* Header */}
      <div className="page-header-row">
        <div>
          <h1 className="page-title">AI Candidate Matching Studio</h1>
          <p className="page-subtitle">
            Perform neural requirement analysis between job specifications and candidate CV intelligence.
          </p>
        </div>
      </div>

      {error && <div className="alert alert-error"><span>⚠️ {error}</span></div>}

      {/* Control Configuration Card */}
      <Card style={{ marginBottom: '24px' }}>
        <Card.Header>
          <Card.Title>Select Evaluation Target</Card.Title>
          <Card.Description>Configure company, job posting, and candidate to compute fit score</Card.Description>
        </Card.Header>
        <Card.Content>
          <div className="matching-controls-grid">
            {/* Company Selector */}
            <div className="form-group">
              <label>Company Workspace</label>
              <select
                value={selectedCompanyId}
                onChange={handleCompanyChange}
                disabled={companies.length === 0}
              >
                {companies.length === 0 ? (
                  <option value="">No companies found</option>
                ) : (
                  companies.map((c) => (
                    <option key={c.id} value={c.id}>
                      🏢 {c.name}
                    </option>
                  ))
                )}
              </select>
            </div>

            {/* Job Selector */}
            <div className="form-group">
              <label>Target Job Opening</label>
              <select
                value={selectedJobId}
                onChange={(e) => setSelectedJobId(e.target.value)}
                disabled={jobs.length === 0}
              >
                {jobs.length === 0 ? (
                  <option value="">No jobs available</option>
                ) : (
                  jobs.map((j) => (
                    <option key={j.id} value={j.id}>
                      💼 {j.title} ({j.status})
                    </option>
                  ))
                )}
              </select>
            </div>

            {/* Candidate / Applicant Selector */}
            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <label style={{ margin: 0 }}>Candidate / Applicant</label>
                <button
                  type="button"
                  onClick={() => setCustomUuidMode(!customUuidMode)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--brand-500)',
                    fontSize: '0.75rem',
                    cursor: 'pointer',
                    textDecoration: 'underline',
                  }}
                >
                  {customUuidMode ? '← Pick from applicants' : '+ Enter custom UUID'}
                </button>
              </div>

              {customUuidMode ? (
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input
                    type="text"
                    placeholder="Paste candidate UUID"
                    value={candidateId}
                    onChange={(e) => setCandidateId(e.target.value)}
                  />
                  {myCandidateId && candidateId !== myCandidateId && (
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setCandidateId(myCandidateId)}
                      title="Use my candidate profile"
                    >
                      Use Mine
                    </Button>
                  )}
                </div>
              ) : (
                <select
                  value={candidateId}
                  onChange={(e) => setCandidateId(e.target.value)}
                  disabled={loadingApplicants || applicants.length === 0}
                >
                  {loadingApplicants ? (
                    <option value="">Loading job applicants...</option>
                  ) : applicants.length === 0 ? (
                    <option value="">No applicants found for this job</option>
                  ) : (
                    applicants.map((app) => (
                      <option key={app.application_id || app.candidate_id} value={app.candidate_id}>
                        👤 {app.candidate_name || 'Candidate'} {app.candidate_email ? `(${app.candidate_email})` : ''} - [{app.status}]
                      </option>
                    ))
                  )}
                </select>
              )}
            </div>
          </div>
        </Card.Content>
        <Card.Footer>
          <Button
            variant="ai"
            size="md"
            icon={Sparkles}
            loading={matching || loading}
            onClick={handleMatch}
          >
            Compute AI Match
          </Button>
        </Card.Footer>
      </Card>

      {/* Results View */}
      {matching ? (
        <Card style={{ textAlign: 'center', padding: '48px 24px' }}>
          <Sparkles size={32} className="ai-sparkle-icon" style={{ color: 'var(--ai-600)', margin: '0 auto 16px' }} />
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Analyzing Candidate Compatibility...</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '4px' }}>
            Evaluating skills, experience, qualifications, and keyword vectors with Groq LLM.
          </p>
        </Card>
      ) : matchResult ? (
        <Card className="matching-results-card">
          {/* AI Banner Notice */}
          <div className="matching-banner">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={16} className="text-ai" />
              <span style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--ai-600)' }}>
                Groq AI Suitability Analysis
              </span>
            </div>
            <div className="matching-review-chip">
              <ShieldAlert size={13} />
              <span>AI Recommendation — Human Review Required</span>
            </div>
          </div>

          <Card.Content style={{ padding: '24px' }}>
            {/* Score & Classification Header */}
            <div className="matching-score-row">
              <ScoreCircle score={matchResult.overall_score || 0} size={90} strokeWidth={8} />
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                  <StatusBadge status={matchResult.classification} />
                  <span style={{ fontSize: '1.25rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                    {Math.round(matchResult.overall_score || 0)}% Overall Score
                  </span>
                </div>
                <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                  {explanation.reasoning || 'Automated multi-factor evaluation completed.'}
                </p>
              </div>
            </div>

            {/* Subscores Grid */}
            <div className="matching-subscores-grid">
              <ScoreBar
                label="Skills Match"
                icon="🛠️"
                score={matchedSkills.length ? Math.min(100, matchedSkills.length * 20) : 25}
              />
              <ScoreBar
                label="Experience Alignment"
                icon="💼"
                score={explanation.experience_match ? 95 : 40}
              />
              <ScoreBar
                label="Education Criteria"
                icon="🎓"
                score={explanation.education_match ? 90 : 35}
              />
              <ScoreBar
                label="Domain & Language"
                icon="🌐"
                score={explanation.language_match ? 95 : 55}
              />
            </div>

            {/* Strengths & Weaknesses Columns */}
            <div className="matching-columns-grid">
              {strengths.length > 0 && (
                <div className="matching-col strength-col">
                  <div className="col-title text-success">
                    <CheckCircle2 size={16} />
                    <span>Candidate Strengths</span>
                  </div>
                  <ul className="col-list">
                    {strengths.map((s, idx) => (
                      <li key={idx}>✓ {s}</li>
                    ))}
                  </ul>
                </div>
              )}

              {weaknesses.length > 0 && (
                <div className="matching-col weakness-col">
                  <div className="col-title text-danger">
                    <AlertCircle size={16} />
                    <span>Potential Growth Areas / Gaps</span>
                  </div>
                  <ul className="col-list">
                    {weaknesses.map((w, idx) => (
                      <li key={idx}>✕ {w}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Matched & Missing Skills Pills */}
            <div style={{ marginTop: '20px' }}>
              <h4 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '10px' }}>Skills Comparison Breakdown</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {matchedSkills.map((sk, idx) => (
                  <span key={idx} className="status-badge badge-success">
                    ✓ {sk}
                  </span>
                ))}
                {missingSkills.map((sk, idx) => (
                  <span key={idx} className="status-badge badge-danger">
                    ✕ {sk}
                  </span>
                ))}
              </div>
            </div>
          </Card.Content>
        </Card>
      ) : (
        <EmptyState
          icon={Sparkles}
          title="Ready to evaluate"
          description="Select a job opening and candidate above, then click 'Compute AI Match' to generate suitability analysis."
        />
      )}
    </div>
  );
}
