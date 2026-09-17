import React from 'react';
import './Card.css';

export default function Card({
  children,
  className = '',
  hover = false,
  onClick,
  ...props
}) {
  return (
    <div
      className={`ui-card ${hover ? 'ui-card-hover' : ''} ${className}`}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  );
}

Card.Header = function CardHeader({ children, className = '', ...props }) {
  return <div className={`ui-card-header ${className}`} {...props}>{children}</div>;
};

Card.Title = function CardTitle({ children, className = '', ...props }) {
  return <h3 className={`ui-card-title ${className}`} {...props}>{children}</h3>;
};

Card.Description = function CardDescription({ children, className = '', ...props }) {
  return <p className={`ui-card-description ${className}`} {...props}>{children}</p>;
};

Card.Content = function CardContent({ children, className = '', ...props }) {
  return <div className={`ui-card-content ${className}`} {...props}>{children}</div>;
};

Card.Footer = function CardFooter({ children, className = '', ...props }) {
  return <div className={`ui-card-footer ${className}`} {...props}>{children}</div>;
};
