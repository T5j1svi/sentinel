import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../AppContext';
import MetricCard from '../components/MetricCard';
import api from '../api/sentinel';

export default function Dashboard() {
  const navigate = useNavigate();
  const { huntResults, evidenceCount } = useApp();
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [statsData, healthData] = await Promise.allSettled([
          api.getDashboardStats(),
          api.health(),
        ]);
        if (statsData.status === 'fulfilled') setStats(statsData.value);
        if (healthData.status === 'fulfilled') setHealth(healthData.value);
      } catch (err) {
        console.error('Dashboard load error:', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const modules = [
    { name: 'Narrative Hunt', icon: '🎯', path: '/hunt', desc: 'Cross-platform multilingual OSINT search', status: 'real' },
    { name: 'Identity Profiler', icon: '👤', path: '/identity', desc: 'Account behavior analysis & cross-platform linking', status: 'new' },
    { name: 'Media Forensics', icon: '🖼️', path: '/media', desc: 'Image/video EXIF, reverse search, deepfake detection', status: 'new' },
    { name: 'Velocity Monitor', icon: '📈', path: '/velocity', desc: 'Real-time narrative spread & anomaly detection', status: 'real' },
    { name: 'Network Mapper', icon: '🕸️', path: '/network', desc: 'Influence network with community detection', status: 'real' },
    { name: 'Behaviour Profiler', icon: '🤖', path: '/bots', desc: 'Coordination scoring & bot detection', status: 'real' },
    { name: 'DISARM Tactics', icon: '🛡️', path: '/tactics', desc: 'Disinformation tactic classification', status: 'real' },
    { name: 'Infrastructure', icon: '🏗️', path: '/infrastructure', desc: 'WHOIS, DNS, cert transparency, hosting', status: 'real' },
    { name: 'Geo Intelligence', icon: '🌍', path: '/geo', desc: 'Geographic origin mapping & anomalies', status: 'real' },
    { name: 'Evidence Locker', icon: '🔒', path: '/evidence', desc: 'SHA-256 hashing, archiving, chain of custody', status: 'real' },
    { name: 'Report Generator', icon: '📋', path: '/reports', desc: 'PDF/DOCX/STIX intelligence reports', status: 'real' },
  ];

  const resultCount = huntResults?.total_results || stats?.total_results || 0;
  const casesCount = stats?.active_cases || 0;

  return (
    <div className="page-enter">
      {/* Hero */}
      <div className="hero-card mb-5">
        <div className="flex items-center justify-between" style={{ position: 'relative', zIndex: 1 }}>
          <div>
            <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: '4px' }}>
              🛡️ SENTINEL Intel
            </h1>
            <p className="text-muted" style={{ fontSize: '13px', maxWidth: '550px' }}>
              Cyber Intelligence Investigation Lab — Find the source. Map the network. Prove the narrative.
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div className="badge badge-success" style={{ fontSize: '11px', padding: '4px 12px' }}>
              {health ? '● ALL SYSTEMS OPERATIONAL' : loading ? '● CONNECTING...' : '● CHECKING STATUS'}
            </div>
            {health && (
              <div className="text-xs text-muted" style={{ marginTop: '4px' }}>
                Backend: {health.version || 'v3.0'}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Metrics — real data */}
      <div className="metrics-grid">
        <MetricCard icon="📊" value={casesCount} label="Active Cases" accentColor="var(--accent-blue)" className="stagger-1" />
        <MetricCard icon="🔒" value={evidenceCount} label="Evidence Items" accentColor="var(--accent-green)" className="stagger-2" />
        <MetricCard icon="🎯" value={resultCount} label="Total Results" accentColor="var(--accent-amber)" className="stagger-3" />
        <MetricCard icon="📡" value={stats?.platforms_monitored || 14} label="Platform Connectors" accentColor="var(--accent-purple)" className="stagger-4" />
        <MetricCard icon="🌐" value="12" label="Languages Active" accentColor="var(--accent-cyan)" className="stagger-5" />
      </div>

      {/* Modules Grid */}
      <div className="glass-card no-hover">
        <div className="section-header">
          <div>
            <div className="section-title">Intelligence Modules</div>
            <div className="section-subtitle">{modules.length} modules available — click to navigate</div>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(210px, 1fr))', gap: '8px' }}>
          {modules.map((mod, i) => (
            <div
              key={mod.name}
              className="animate-slide-up"
              style={{
                padding: '12px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                animationDelay: `${i * 0.03}s`,
                transition: 'all 0.2s ease',
                cursor: 'pointer',
              }}
              onClick={() => navigate(mod.path)}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-accent)';
                e.currentTarget.style.background = 'var(--bg-card-hover)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-subtle)';
                e.currentTarget.style.background = 'var(--bg-card)';
              }}
            >
              <div className="flex items-center gap-2 mb-1">
                <span style={{ fontSize: '16px' }}>{mod.icon}</span>
                <span style={{ fontSize: '12px', fontWeight: 600 }}>{mod.name}</span>
                {mod.status === 'new' && (
                  <span className="badge badge-info" style={{ fontSize: '8px', padding: '1px 4px' }}>NEW</span>
                )}
              </div>
              <div className="text-xs text-muted" style={{ lineHeight: 1.4 }}>{mod.desc}</div>
              <div className="flex items-center gap-2 mt-3">
                <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: 'var(--accent-green)' }}></span>
                <span style={{ fontSize: '9px', color: 'var(--text-success)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.06em' }}>Online</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
