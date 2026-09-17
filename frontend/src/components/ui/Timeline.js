import React from 'react';
import { CheckCircle2, Clock, XCircle, Sparkles, Calendar, Award } from 'lucide-react';
import './Timeline.css';

const STAGES = [
  { key: 'APPLIED', label: 'Applied', icon: Clock },
  { key: 'AI_SCREENING', label: 'AI Screened', icon: Sparkles },
  { key: 'SHORTLISTED', label: 'Shortlisted', icon: CheckCircle2 },
  { key: 'INTERVIEWING', label: 'Interview', icon: Calendar },
  { key: 'OFFERED', label: 'Offer', icon: Award },
  { key: 'HIRED', label: 'Hired', icon: CheckCircle2 },
];

export default function Timeline({ currentStatus = 'APPLIED', isRejected = false }) {
  const norm = currentStatus.toUpperCase().replace(/\s+/g, '_');
  const rejected = isRejected || norm === 'REJECTED';

  const getStageIndex = (status) => {
    switch (status) {
      case 'APPLIED': return 0;
      case 'AI_SCREENING': return 1;
      case 'SHORTLISTED': return 2;
      case 'INTERVIEWING': return 3;
      case 'OFFERED': return 4;
      case 'HIRED': return 5;
      default: return 0;
    }
  };

  const currentIndex = getStageIndex(norm);

  return (
    <div className="hiring-timeline-root">
      <div className="hiring-timeline-track">
        {STAGES.map((stage, idx) => {
          const isPast = idx < currentIndex;
          const isCurrent = idx === currentIndex && !rejected;
          const Icon = stage.icon;

          let stepClass = 'step-future';
          if (isPast) stepClass = 'step-completed';
          if (isCurrent) stepClass = 'step-current';

          return (
            <div key={stage.key} className={`timeline-step ${stepClass}`}>
              <div className="timeline-node">
                <Icon size={14} className="timeline-node-icon" />
              </div>
              <span className="timeline-label">{stage.label}</span>
              {idx < STAGES.length - 1 && (
                <div
                  className={`timeline-connector ${
                    idx < currentIndex ? 'connector-active' : ''
                  }`}
                />
              )}
            </div>
          );
        })}

        {rejected && (
          <div className="timeline-step step-rejected">
            <div className="timeline-node">
              <XCircle size={14} className="timeline-node-icon" />
            </div>
            <span className="timeline-label">Rejected</span>
          </div>
        )}
      </div>
    </div>
  );
}
