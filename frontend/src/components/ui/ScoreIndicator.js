import React from 'react';
import './ScoreIndicator.css';

export function getScoreColor(score) {
  if (score >= 80) return 'var(--success-500)';
  if (score >= 65) return 'var(--brand-500)';
  if (score >= 50) return 'var(--warning-500)';
  return 'var(--danger-500)';
}

export function ScoreCircle({ score = 0, size = 64, strokeWidth = 6, showLabel = true }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clampedScore = Math.max(0, Math.min(100, Math.round(score)));
  const offset = circumference - (clampedScore / 100) * circumference;
  const color = getScoreColor(clampedScore);

  return (
    <div className="score-circle-wrapper" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="score-circle-svg">
        <circle
          className="score-circle-bg"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
        />
        <circle
          className="score-circle-progress"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          stroke={color}
        />
      </svg>
      <div className="score-circle-text">
        <span className="score-value" style={{ color }}>{clampedScore}%</span>
        {showLabel && size >= 70 && <span className="score-subtext">Match</span>}
      </div>
    </div>
  );
}

export function ScoreBar({ label, score = 0, max = 100, icon, showPercent = true }) {
  const percent = Math.min(100, Math.max(0, Math.round((score / max) * 100)));
  const color = getScoreColor(percent);

  return (
    <div className="score-bar-item">
      <div className="score-bar-header">
        <span className="score-bar-label">
          {icon && <span className="score-bar-icon">{icon}</span>}
          {label}
        </span>
        {showPercent && (
          <span className="score-bar-value" style={{ color }}>{percent}%</span>
        )}
      </div>
      <div className="score-bar-track">
        <div
          className="score-bar-fill"
          style={{ width: `${percent}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}
