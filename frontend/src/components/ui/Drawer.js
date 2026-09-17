import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import './Drawer.css';

export default function Drawer({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  width = '520px',
  footer,
}) {
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="drawer-root">
          <motion.div
            className="drawer-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
          />
          <motion.div
            className="drawer-panel"
            style={{ width }}
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 28, stiffness: 300 }}
          >
            <div className="drawer-header">
              <div>
                <h3 className="drawer-title">{title}</h3>
                {subtitle && <p className="drawer-subtitle">{subtitle}</p>}
              </div>
              <button
                type="button"
                className="drawer-close-btn"
                onClick={onClose}
                aria-label="Close drawer"
              >
                <X size={20} />
              </button>
            </div>

            <div className="drawer-content">{children}</div>

            {footer && <div className="drawer-footer">{footer}</div>}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
