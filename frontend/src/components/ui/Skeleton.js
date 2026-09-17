import React from 'react';
import './Skeleton.css';

export default function Skeleton({
  variant = 'text',
  width,
  height,
  className = '',
  count = 1,
}) {
  const elements = Array.from({ length: count });

  return (
    <>
      {elements.map((_, i) => (
        <div
          key={i}
          className={`ui-skeleton skeleton-${variant} ${className}`}
          style={{
            width: width || (variant === 'circle' ? height : undefined),
            height: height || (variant === 'circle' ? width : undefined),
          }}
        />
      ))}
    </>
  );
}

export function SkeletonCard() {
  return (
    <div className="skeleton-card-wrapper">
      <div className="skeleton-card-header">
        <Skeleton variant="circle" width={40} height={40} />
        <div style={{ flex: 1 }}>
          <Skeleton variant="text" width="60%" height={16} />
          <Skeleton variant="text" width="40%" height={12} style={{ marginTop: 6 }} />
        </div>
      </div>
      <div style={{ marginTop: 16 }}>
        <Skeleton variant="rect" width="100%" height={48} />
      </div>
    </div>
  );
}
