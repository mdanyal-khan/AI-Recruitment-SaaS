import React from 'react';
import Button from './Button';
import './EmptyState.css';

export default function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
  actionIcon,
  className = '',
}) {
  return (
    <div className={`empty-state-root ${className}`}>
      {Icon && (
        <div className="empty-state-icon-box">
          <Icon size={28} className="empty-state-icon" />
        </div>
      )}
      <h4 className="empty-state-title">{title}</h4>
      {description && <p className="empty-state-description">{description}</p>}
      {actionLabel && onAction && (
        <div className="empty-state-action">
          <Button variant="primary" size="md" onClick={onAction} icon={actionIcon}>
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
}
