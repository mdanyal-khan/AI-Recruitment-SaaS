import React from 'react';
import './Input.css';

export function Input({
  label,
  error,
  helper,
  icon: Icon,
  className = '',
  id,
  required,
  ...props
}) {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className={`input-field-group ${className}`}>
      {label && (
        <label htmlFor={inputId} className="input-label">
          {label} {required && <span className="input-required">*</span>}
        </label>
      )}
      <div className="input-wrapper">
        {Icon && <Icon size={16} className="input-leading-icon" />}
        <input
          id={inputId}
          className={`input-control ${Icon ? 'input-has-icon' : ''} ${error ? 'input-error' : ''}`}
          required={required}
          {...props}
        />
      </div>
      {error && <span className="input-error-msg">{error}</span>}
      {helper && !error && <span className="input-helper-msg">{helper}</span>}
    </div>
  );
}

export function Select({
  label,
  error,
  helper,
  children,
  className = '',
  id,
  required,
  ...props
}) {
  const selectId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className={`input-field-group ${className}`}>
      {label && (
        <label htmlFor={selectId} className="input-label">
          {label} {required && <span className="input-required">*</span>}
        </label>
      )}
      <div className="select-wrapper">
        <select
          id={selectId}
          className={`select-control ${error ? 'input-error' : ''}`}
          required={required}
          {...props}
        >
          {children}
        </select>
      </div>
      {error && <span className="input-error-msg">{error}</span>}
      {helper && !error && <span className="input-helper-msg">{helper}</span>}
    </div>
  );
}

export function Textarea({
  label,
  error,
  helper,
  className = '',
  id,
  required,
  rows = 4,
  ...props
}) {
  const textareaId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className={`input-field-group ${className}`}>
      {label && (
        <label htmlFor={textareaId} className="input-label">
          {label} {required && <span className="input-required">*</span>}
        </label>
      )}
      <textarea
        id={textareaId}
        rows={rows}
        className={`textarea-control ${error ? 'input-error' : ''}`}
        required={required}
        {...props}
      />
      {error && <span className="input-error-msg">{error}</span>}
      {helper && !error && <span className="input-helper-msg">{helper}</span>}
    </div>
  );
}
