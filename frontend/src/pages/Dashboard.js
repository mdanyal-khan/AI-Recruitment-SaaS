import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import {
  companiesAPI,
  jobsAPI,
  resumesAPI,
  applicationsAPI,
  interviewsAPI,
  candidateOffersAPI,
} from '../services/api';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Timeline from '../components/ui/Timeline';
import { SkeletonCard } from '../components/ui/Skeleton';
import {
  Briefcase,
  FileText,
  Sparkles,
  Calendar,
  Award,
  Building,
  ArrowRight,
} from 'lucide-react';
import './Dashboard.css';

export default function Dashboard() {
  const { user } = useAuth();
  const isRecruiter = ['OWNER', 'HR', 'RECRUITER', 'COMPANY_ADMIN'].includes(
    user?.role?.toUpperCase()
  );

  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    companiesCount: 0,
    jobsCount: 0,
    resumesCount: 0,
    candidateApplicationsCount: 0,
    candidateInterviewsCount: 0,
    candidateOffersCount: 0,
  });

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        if (isRecruiter) {
          const [compRes, resumeRes] = await Promise.allSettled([
            companiesAPI.list(),
            resumesAPI.list(),
          ]);

          const comps = compRes.status === 'fulfilled' ? compRes.value.data : [];
          let totalJobs = 0;

          if (comps.length > 0) {
            try {
              const jobsRes = await jobsAPI.list(comps[0].id);
              totalJobs = jobsRes.data.length;
            } catch (e) {
              // Non-fatal
            }
          }

          setStats({
            companiesCount: comps.length,
            jobsCount: totalJobs,
            resumesCount: resumeRes.status === 'fulfilled' ? resumeRes.value.data.length : 0,
            candidateApplicationsCount: 0,
            candidateInterviewsCount: 0,
            candidateOffersCount: 0,
          });
        } else {
          // Candidate view metrics
          const [resumeRes, appRes, interviewRes, offerRes] = await Promise.allSettled([
            resumesAPI.list(),
            applicationsAPI.getMyApplications(),
            interviewsAPI.getMyInterviews(),
            candidateOffersAPI.list(),
          ]);

          setStats({
            companiesCount: 0,
            jobsCount: 0,
            resumesCount: resumeRes.status === 'fulfilled' ? resumeRes.value.data.length : 0,
            candidateApplicationsCount:
              appRes.status === 'fulfilled' ? (appRes.value.data?.length || 0) : 0,
            candidateInterviewsCount:
              interviewRes.status === 'fulfilled'
                ? (Array.isArray(interviewRes.value.data)
                    ? interviewRes.value.data.length
                    : interviewRes.value.data?.interviews?.length || 0)
                : 0,
            candidateOffersCount:
              offerRes.status === 'fulfilled' ? (offerRes.value.data?.length || 0) : 0,
          });
        }
      } catch (err) {
        // Handled gracefully
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [isRecruiter]);

  return (
    <div className="dashboard-root">
      {/* Hero Welcome Header */}
      <section className="dashboard-hero-header">
        <div className="hero-text-block">
          <div className="hero-eyebrow">
            <Sparkles size={14} className="sparkle-icon" />
            <span>AI Talent Intelligence Platform</span>
          </div>
          <h1 className="hero-headline">
            Welcome back, {user?.first_name || 'Recruiter'} 👋
          </h1>
          <p className="hero-subline">
            {isRecruiter
              ? 'Real-time hiring orchestration, automated CV evaluation, and high-precision candidate matching.'
              : 'Track your job applications, schedule interviews, and manage formal job offers in one place.'}
          </p>
        </div>

        <div className="hero-account-badge">
          <div className="account-avatar-circle">
            {user?.first_name ? user.first_name[0].toUpperCase() : 'U'}
          </div>
          <div className="account-info-meta">
            <span className="account-email">{user?.email}</span>
            <span className="account-role-tag">{user?.role}</span>
          </div>
        </div>
      </section>

      {/* KPI Metrics Grid */}
      <section className="kpi-metrics-grid">
        {loading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : isRecruiter ? (
          <>
            <Card hover>
              <Card.Header>
                <div className="kpi-header-row">
                  <span className="kpi-label">Companies</span>
                  <div className="kpi-icon-box bg-purple">
                    <Building size={18} />
                  </div>
                </div>
                <div className="kpi-number">{stats.companiesCount}</div>
                <Card.Description>Workspaces managed by your account</Card.Description>
              </Card.Header>
            </Card>

            <Card hover>
              <Card.Header>
                <div className="kpi-header-row">
                  <span className="kpi-label">Active Job Openings</span>
                  <div className="kpi-icon-box bg-blue">
                    <Briefcase size={18} />
                  </div>
                </div>
                <div className="kpi-number">{stats.jobsCount}</div>
                <Card.Description>Published roles seeking talent</Card.Description>
              </Card.Header>
            </Card>

            <Card hover>
              <Card.Header>
                <div className="kpi-header-row">
                  <span className="kpi-label">Resumes in Talent Pool</span>
                  <div className="kpi-icon-box bg-emerald">
                    <FileText size={18} />
                  </div>
                </div>
                <div className="kpi-number">{stats.resumesCount}</div>
                <Card.Description>Processed and analyzed CVs</Card.Description>
              </Card.Header>
            </Card>

            <Card hover>
              <Card.Header>
                <div className="kpi-header-row">
                  <span className="kpi-label">AI Engine Status</span>
                  <div className="kpi-icon-box bg-violet">
                    <Sparkles size={18} />
                  </div>
                </div>
                <div className="kpi-number text-ai">Groq 70B</div>
                <Card.Description>Neural CV parsing & matching active</Card.Description>
              </Card.Header>
            </Card>
          </>
        ) : (
          <>
            <Card hover>
              <Card.Header>
                <div className="kpi-header-row">
                  <span className="kpi-label">My Applications</span>
                  <div className="kpi-icon-box bg-blue">
                    <Briefcase size={18} />
                  </div>
                </div>
                <div className="kpi-number">{stats.candidateApplicationsCount}</div>
                <Card.Description>Active job applications</Card.Description>
              </Card.Header>
            </Card>

            <Card hover>
              <Card.Header>
                <div className="kpi-header-row">
                  <span className="kpi-label">Scheduled Interviews</span>
                  <div className="kpi-icon-box bg-purple">
                    <Calendar size={18} />
                  </div>
                </div>
                <div className="kpi-number">{stats.candidateInterviewsCount}</div>
                <Card.Description>Upcoming interviews</Card.Description>
              </Card.Header>
            </Card>

            <Card hover>
              <Card.Header>
                <div className="kpi-header-row">
                  <span className="kpi-label">Job Offers</span>
                  <div className="kpi-icon-box bg-emerald">
                    <Award size={18} />
                  </div>
                </div>
                <div className="kpi-number">{stats.candidateOffersCount}</div>
                <Card.Description>Pending and received offers</Card.Description>
              </Card.Header>
            </Card>

            <Card hover>
              <Card.Header>
                <div className="kpi-header-row">
                  <span className="kpi-label">Uploaded CVs</span>
                  <div className="kpi-icon-box bg-violet">
                    <FileText size={18} />
                  </div>
                </div>
                <div className="kpi-number">{stats.resumesCount}</div>
                <Card.Description>AI Analyzed Profile Resumes</Card.Description>
              </Card.Header>
            </Card>
          </>
        )}
      </section>

      {/* Visual Hiring Pipeline Banner (Recruiter & Candidate) */}
      <section className="dashboard-pipeline-banner">
        <Card>
          <Card.Header>
            <div className="pipeline-header-flex">
              <div>
                <Card.Title>Automated Recruitment Lifecycle</Card.Title>
                <Card.Description>
                  Continuous progression from initial candidate application to final hire.
                </Card.Description>
              </div>
              <Link to={isRecruiter ? '/jobs' : '/jobs'}>
                <Button variant="outline" size="sm" icon={ArrowRight} iconPosition="right">
                  {isRecruiter ? 'Manage Pipeline' : 'Browse Openings'}
                </Button>
              </Link>
            </div>
          </Card.Header>
          <Card.Content>
            <Timeline currentStatus="SHORTLISTED" />
          </Card.Content>
        </Card>
      </section>

      {/* Quick Launch Workspaces Grid */}
      <section className="dashboard-modules-section">
        <div className="section-title-wrap">
          <h2>Core Workspace Modules</h2>
          <p>Quick access to your core recruiting workflows and talent tools</p>
        </div>

        <div className="modules-card-grid">
          <Link to="/jobs" className="workspace-card">
            <div className="workspace-icon bg-blue">
              <Briefcase size={22} />
            </div>
            <div className="workspace-meta">
              <h3>{isRecruiter ? 'Jobs & Applicant Pipeline' : 'Find Job Openings'}</h3>
              <p>
                {isRecruiter
                  ? 'Create openings, manage publishing, screen applicants, and extend formal offers.'
                  : 'Explore available developer and engineering roles and apply with 1-click.'}
              </p>
            </div>
            <span className="workspace-arrow">→</span>
          </Link>

          <Link to="/matching" className="workspace-card card-ai-featured">
            <div className="workspace-badge-chip">AI Engine</div>
            <div className="workspace-icon bg-violet">
              <Sparkles size={22} />
            </div>
            <div className="workspace-meta">
              <h3>AI Candidate Matcher</h3>
              <p>
                Compare resumes against job requirements with instant multi-factor scoring.
              </p>
            </div>
            <span className="workspace-arrow">→</span>
          </Link>

          <Link to="/interviews" className="workspace-card">
            <div className="workspace-icon bg-purple">
              <Calendar size={22} />
            </div>
            <div className="workspace-meta">
              <h3>Interviews & Calendar</h3>
              <p>
                {isRecruiter
                  ? 'Schedule interview sessions, record notes, and submit hiring recommendations.'
                  : 'View meeting schedules, meeting links, and confirm attendance.'}
              </p>
            </div>
            <span className="workspace-arrow">→</span>
          </Link>

          <Link to="/offers" className="workspace-card">
            <div className="workspace-icon bg-emerald">
              <Award size={22} />
            </div>
            <div className="workspace-meta">
              <h3>Offers & Hiring</h3>
              <p>
                {isRecruiter
                  ? 'Generate compensation packages, track candidate responses, and finalize hires.'
                  : 'Review received job offers, compensation details, and accept offers.'}
              </p>
            </div>
            <span className="workspace-arrow">→</span>
          </Link>

          <Link to="/resumes" className="workspace-card">
            <div className="workspace-icon bg-amber">
              <FileText size={22} />
            </div>
            <div className="workspace-meta">
              <h3>Resume Intelligence Pool</h3>
              <p>
                Upload candidate PDFs, extract skill profiles with PyPDF & Groq, and download files.
              </p>
            </div>
            <span className="workspace-arrow">→</span>
          </Link>

          {isRecruiter && (
            <Link to="/companies" className="workspace-card">
              <div className="workspace-icon bg-cyan">
                <Building size={22} />
              </div>
              <div className="workspace-meta">
                <h3>Company Workspace</h3>
                <p>
                  Configure company branding, invite recruitment team members, and assign roles.
                </p>
              </div>
              <span className="workspace-arrow">→</span>
            </Link>
          )}
        </div>
      </section>
    </div>
  );
}
