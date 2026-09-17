import React from 'react';
import { Sparkles, CheckCircle2, AlertCircle, ShieldAlert } from 'lucide-react';
import { ScoreCircle, ScoreBar } from '../ui/ScoreIndicator';
import StatusBadge from '../ui/StatusBadge';
import Card from '../ui/Card';
import './AIScreeningCard.css';

export default function AIScreeningCard({ screeningResult, className = '' }) {
  if (!screeningResult) return null;

  const score = screeningResult.overall_match_score || screeningResult.match_score || 0;
  const classification = screeningResult.classification || 'PARTIAL_MATCH';
  const subscores = screeningResult.subscores || screeningResult.score_breakdown || {};
  const strengths = screeningResult.strengths || [];
  const gaps = screeningResult.missing_skills || screeningResult.potential_gaps || [];
  const reasoning = screeningResult.reasoning || screeningResult.summary || '';

  return (
    <Card className={`ai-screening-card ${className}`}>
      {/* AI Header with Notice */}
      <div className="ai-card-banner">
        <div className="ai-badge-chip">
          <Sparkles size={14} className="ai-sparkle-icon" />
          <span>Groq AI Screening Intelligence</span>
        </div>
        <div className="ai-human-review-note">
          <ShieldAlert size={13} />
          <span>AI Recommendation — Human Review Required</span>
        </div>
      </div>

      <Card.Content className="ai-card-body">
        {/* Score & Classification Overview */}
        <div className="ai-score-overview">
          <ScoreCircle score={score} size={84} strokeWidth={8} />
          <div className="ai-meta-block">
            <div className="ai-classification-row">
              <StatusBadge status={classification} />
              <span className="ai-score-number">{Math.round(score)} / 100</span>
            </div>
            <p className="ai-summary-text">
              {reasoning || 'Automated CV analysis and requirement comparison completed successfully.'}
            </p>
          </div>
        </div>

        {/* Subscores Grid */}
        <div className="ai-subscores-grid">
          <ScoreBar label="Skills Match" score={subscores.skills_match || subscores.skills || 0} icon="🛠️" />
          <ScoreBar label="Experience Relevance" score={subscores.experience_match || subscores.experience || 0} icon="📈" />
          <ScoreBar label="Education Alignment" score={subscores.education_match || subscores.education || 0} icon="🎓" />
          <ScoreBar label="Keyword Relevance" score={subscores.keyword_match || subscores.keywords || 0} icon="🔍" />
        </div>

        {/* Strengths & Missing Skills */}
        <div className="ai-skills-breakdown">
          {strengths.length > 0 && (
            <div className="ai-skill-col">
              <div className="ai-col-header text-success">
                <CheckCircle2 size={15} />
                <span>Identified Strengths</span>
              </div>
              <div className="ai-skill-pills">
                {strengths.map((s, idx) => (
                  <span key={idx} className="ai-pill pill-strength">{s}</span>
                ))}
              </div>
            </div>
          )}

          {gaps.length > 0 && (
            <div className="ai-skill-col">
              <div className="ai-col-header text-warning">
                <AlertCircle size={15} />
                <span>Skills to Probe / Gaps</span>
              </div>
              <div className="ai-skill-pills">
                {gaps.map((g, idx) => (
                  <span key={idx} className="ai-pill pill-gap">{g}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </Card.Content>
    </Card>
  );
}
