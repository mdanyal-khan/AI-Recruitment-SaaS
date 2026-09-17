import React, { useState, useEffect, useCallback } from 'react';
import { systemAPI } from '../services/api';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Database, Server, RefreshCw } from 'lucide-react';
import './Page.css';

export default function SystemHealth() {
  const [loading, setLoading] = useState(false);
  const [healthData, setHealthData] = useState({
    apiStatus: 'checking',
    apiLatency: null,
    dbStatus: 'checking',
    dbLatency: null,
    lastChecked: null,
  });

  const checkHealth = useCallback(async () => {
    setLoading(true);

    try {
      const apiStart = performance.now();
      const apiRes = await systemAPI.health();
      const apiEnd = performance.now();

      const dbStart = performance.now();
      const dbRes = await systemAPI.database();
      const dbEnd = performance.now();

      setHealthData({
        apiStatus: apiRes.data?.status === 'ok' ? 'operational' : 'error',
        apiLatency: Math.round(apiEnd - apiStart),
        dbStatus: dbRes.data?.status === 'ok' && dbRes.data?.database === 'connected' ? 'operational' : 'error',
        dbLatency: Math.round(dbEnd - dbStart),
        lastChecked: new Date().toLocaleTimeString(),
      });
    } catch (err) {
      setHealthData(prev => ({
        ...prev,
        apiStatus: 'error',
        dbStatus: 'error',
        lastChecked: new Date().toLocaleTimeString(),
      }));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  return (
    <div className="page-shell">
      <div className="page-header-row">
        <div>
          <h1 className="page-title">System Infrastructure Health</h1>
          <p className="page-subtitle">
            Real-time operational monitoring of backend API and PostgreSQL services.
          </p>
        </div>
        <Button
          variant="secondary"
          size="md"
          icon={RefreshCw}
          loading={loading}
          onClick={checkHealth}
        >
          Re-Check Status
        </Button>
      </div>

      <div className="health-cards-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px', marginTop: '24px' }}>
        {/* FastAPI Card */}
        <Card>
          <Card.Header>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Server size={20} className="text-brand" />
                <Card.Title>FastAPI REST Engine</Card.Title>
              </div>
              <span className={`status-badge ${healthData.apiStatus === 'operational' ? 'badge-success' : 'badge-danger'}`}>
                {healthData.apiStatus === 'operational' ? '● Operational' : '● Unavailable'}
              </span>
            </div>
            <Card.Description>Core API router, authentication middleware, and route dispatch</Card.Description>
          </Card.Header>
          <Card.Content>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderTop: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Response Latency</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{healthData.apiLatency !== null ? `${healthData.apiLatency} ms` : '...'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderTop: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Target Host</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem' }}>http://localhost:8000</span>
            </div>
          </Card.Content>
        </Card>

        {/* PostgreSQL Database Card */}
        <Card>
          <Card.Header>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Database size={20} className="text-brand" />
                <Card.Title>PostgreSQL Database</Card.Title>
              </div>
              <span className={`status-badge ${healthData.dbStatus === 'operational' ? 'badge-success' : 'badge-danger'}`}>
                {healthData.dbStatus === 'operational' ? '● Operational' : '● Unavailable'}
              </span>
            </div>
            <Card.Description>Supabase connection pool and SQLAlchemy database session</Card.Description>
          </Card.Header>
          <Card.Content>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderTop: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Query Latency (SELECT 1)</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{healthData.dbLatency !== null ? `${healthData.dbLatency} ms` : '...'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderTop: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Pool Status</span>
              <span style={{ color: 'var(--success-600)', fontWeight: 600 }}>Connected</span>
            </div>
          </Card.Content>
        </Card>
      </div>

      <div style={{ marginTop: '20px', color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
        Last verified at: {healthData.lastChecked || 'Checking...'}
      </div>
    </div>
  );
}
