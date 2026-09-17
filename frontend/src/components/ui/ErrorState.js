import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import Button from './Button';
import './ErrorState.css';

export default function ErrorState({
  statusCode,
  message,
  onRetry,
  className = '',
}) {
  let title = 'Something went wrong';
  let description = message || 'An unexpected error occurred while loading this data.';

  if (statusCode === 401) {
    title = 'Authentication Required';
    description = 'Your session has expired. Please log in again to continue.';
  } else if (statusCode === 403) {
    title = 'Access Denied';
    description = 'You do not have permission to perform this action or view this resource.';
  } else if (statusCode === 404) {
    title = 'Resource Not Found';
    description = 'The requested resource could not be found or may have been deleted.';
  } else if (statusCode >= 500) {
    title = 'Server Error';
    description = 'Something went wrong on the server. Please try again in a moment.';
  }

  return (
    <div className={`error-state-root ${className}`}>
      <div className="error-state-icon-box">
        <AlertTriangle size={28} className="error-state-icon" />
      </div>
      <h4 className="error-state-title">{title}</h4>
      <p className="error-state-description">{description}</p>
      {onRetry && (
        <div className="error-state-action">
          <Button variant="secondary" size="md" onClick={onRetry} icon={RefreshCw}>
            Try Again
          </Button>
        </div>
      )}
    </div>
  );
}
