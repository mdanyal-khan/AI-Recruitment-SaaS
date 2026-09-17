import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import './Button.css';

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  icon: Icon,
  iconPosition = 'left',
  className = '',
  onClick,
  type = 'button',
  ...props
}) {
  return (
    <motion.button
      type={type}
      whileHover={!disabled && !loading ? { scale: 1.01 } : {}}
      whileTap={!disabled && !loading ? { scale: 0.98 } : {}}
      transition={{ duration: 0.12 }}
      disabled={disabled || loading}
      onClick={onClick}
      className={`btn-base btn-${variant} btn-${size} ${loading ? 'btn-loading' : ''} ${className}`}
      {...props}
    >
      {loading ? (
        <Loader2 className="btn-spinner" size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />
      ) : (
        Icon && iconPosition === 'left' && <Icon className="btn-icon-left" size={size === 'sm' ? 14 : 16} />
      )}
      <span className="btn-text">{children}</span>
      {!loading && Icon && iconPosition === 'right' && (
        <Icon className="btn-icon-right" size={size === 'sm' ? 14 : 16} />
      )}
    </motion.button>
  );
}
