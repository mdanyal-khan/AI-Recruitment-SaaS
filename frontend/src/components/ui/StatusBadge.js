import React from 'react';
import './StatusBadge.css';

export default function StatusBadge({ status, type = 'default', className = '' }) {
  if (!status) return null;

  const normalized = status.toUpperCase().replace(/\s+/g, '_');

  let variant = 'neutral';
  let label = status;

  switch (normalized) {
    // Success / High states
    case 'PUBLISHED':
    case 'HIRED':
    case 'ACCEPTED':
    case 'COMPLETED':
    case 'CONFIRMED':
    case 'STRONG_MATCH':
      variant = 'success';
      if (normalized === 'STRONG_MATCH') label = 'Strong Match';
      break;

    // Warning / Active evaluation
    case 'SHORTLISTED':
    case 'INTERVIEWING':
    case 'SENT':
    case 'GOOD_MATCH':
      variant = 'info';
      if (normalized === 'GOOD_MATCH') label = 'Good Match';
      break;

    // In-progress / AI
    case 'AI_SCREENING':
    case 'AI SCREENING':
    case 'PARTIAL_MATCH':
      variant = 'ai';
      if (normalized.includes('AI')) label = 'AI Screening';
      if (normalized === 'PARTIAL_MATCH') label = 'Partial Match';
      break;

    case 'OFFERED':
    case 'SCHEDULED':
    case 'PENDING':
    case 'DRAFT':
      variant = 'warning';
      break;

    // Danger / Negative states
    case 'REJECTED':
    case 'DECLINED':
    case 'CANCELLED':
    case 'NO_SHOW':
    case 'CLOSED':
    case 'NOT_A_MATCH':
    case 'WEAK_MATCH':
      variant = 'danger';
      if (normalized === 'NO_SHOW') label = 'No Show';
      if (normalized === 'WEAK_MATCH') label = 'Weak Match';
      if (normalized === 'NOT_A_MATCH') label = 'Not A Match';
      break;

    case 'ARCHIVED':
    default:
      variant = 'neutral';
      break;
  }

  return (
    <span className={`status-badge badge-${variant} ${className}`}>
      <span className="badge-dot" />
      {label}
    </span>
  );
}
