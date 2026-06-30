import { useState, useEffect } from 'react';
import MetricCard from '../components/MetricCard';
import api from '../api/sentinel';

export default function Velocity() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('7d');
  const [narrative, setNarrative] = useState('');

  const loadVelocity = async (query = '') => {
    setLoading(true);
    try {
      const hours = { '24h': 24, '7d': 168, '30d': 720 }[timeRange] || 168;
      const result = await api.getVelocity('default', query || 'Active monitoring', hours);
      setData(result);
    } catch (err) {
      console.error('Velocity load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadVelocity(narrative); }, [timeRange]);

  const runMockAnalysis = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setData({
        peak_velocity: 340,
        anomalies: [{ timestamp: new Date().toISOString(), platform: 'Twitter', count: 340 }],
        data_points: [
          { count: 2, is_anomaly: false },
          { count: 45, is_anomaly: false },
          { count: 120, is_anomaly: false },
          { count: 340, is_anomaly: true }
        ],
        current_trend: 'spike_detected'
      });
    }, 2000);
  };

  const renderChart = () => {
    if (!data || !data.data_points || data.data_points.length === 0) return null;

    const points = data.data_points;
    const maxCount = Math.max(...points.map(p => p.count), 1);
    const chartWidth = 800;
    const chartHeight = 260;
    const padding = 50;

    // Build SVG area chart path
    const xStep = (chartWidth - padding) / Math.max(points.length - 1, 1);
    const getY = (count) => chartHeight - padding - ((count / maxCount) * (chartHeight - padding - 10));

    let linePath = '';
    let areaPath = '';
    points.forEach((p, i) => {
      const x = padding + i * xStep;
      const y = getY(p.count);
      if (i === 0) {
        linePath += `M ${x} ${y}`;
        areaPath += `M ${x} ${chartHeight - padding}  L ${x} ${y}`;
      } else {
        linePath += ` L ${x} ${y}`;
        areaPath += ` L ${x} ${y}`;
      }
    });
    areaPath += ` L ${padding + (points.length - 1) * xStep} ${chartHeight - padding} Z`;

    return (
      <div style={{ position: 'relative', height: `${chartHeight}px`, overflow: 'hidden' }}>
        <svg width="100%" height="100%" viewBox={`0 0 ${chartWidth} ${chartHeight}`} preserveAspectRatio="none">
          {/* Grid lines */}
          {[0.25, 0.5, 0.75, 1].map(frac => {
            const y = getY(maxCount * frac);
            return (
              <g key={frac}>
                <line x1={padding} y1={y} x2={chartWidth} y2={y} stroke="var(--border-subtle)" strokeWidth="0.5" strokeDasharray="4,4" />
                <text x={padding - 6} y={y + 4} textAnchor="end" fill="var(--text-muted)" fontSize="9" fontFamily="JetBrains Mono">
                  {Math.round(maxCount * frac)}
                </text>
              </g>
            );
          })}
          {/* Baseline */}
          <line x1={padding} y1={chartHeight - padding} x2={chartWidth} y2={chartHeight - padding} stroke="var(--border-subtle)" strokeWidth="0.5" />

          {/* Area fill */}
          <defs>
            <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--accent-blue)" stopOpacity="0.2" />
              <stop offset="100%" stopColor="var(--accent-blue)" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="anomalyGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--accent-red)" stopOpacity="0.15" />
              <stop offset="100%" stopColor="var(--accent-red)" stopOpacity="0" />
            </linearGradient>
          </defs>
          <path d={areaPath} fill="url(#areaGrad)" />
          <path d={linePath} fill="none" stroke="var(--accent-blue)" strokeWidth="1.5" />

          {/* Anomaly dots */}
          {points.map((p, i) => {
            if (!p.is_anomaly) return null;
            const x = padding + i * xStep;
            const y = getY(p.count);
            return (
              <g key={`a-${i}`}>
                <circle cx={x} cy={y} r="6" fill="var(--accent-red)" opacity="0.15">
                  <animate attributeName="r" from="4" to="12" dur="2s" repeatCount="indefinite" />
                  <animate attributeName="opacity" from="0.3" to="0" dur="2s" repeatCount="indefinite" />
                </circle>
                <circle cx={x} cy={y} r="3" fill="var(--accent-red)" />
              </g>
            );
          })}
        </svg>
      </div>
    );
  };

  return (
    <div className="page-enter">
      <div className="glass-card mb-5">
        <div className="section-header">
          <div>
            <div className="section-title">📈 Velocity Monitor</div>
            <div className="section-subtitle">Track narrative spread velocity across platforms. Detect coordinated amplification spikes.</div>
          </div>
          <div className="flex items-center gap-3">
            <div className="search-bar" style={{ width: '260px' }}>
              <input
                type="text"
                value={narrative}
                onChange={(e) => setNarrative(e.target.value)}
                placeholder="Track narrative..."
                onKeyDown={(e) => e.key === 'Enter' && loadVelocity(narrative)}
                style={{ padding: '7px 12px', fontSize: '12px' }}
              />
            </div>
            <div className="tab-group">
              {['24h', '7d', '30d'].map(range => (
                <button
                  key={range}
                  className={`tab-item ${timeRange === range ? 'active' : ''}`}
                  onClick={() => setTimeRange(range)}
                >
                  {range}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {data && (
        <>
          <div className="metrics-grid">
            <MetricCard icon="🚀" value={data.peak_velocity} label="Peak Velocity" accentColor="var(--accent-red)" />
            <MetricCard icon="⚠️" value={data.anomalies?.length || 0} label="Anomalies" accentColor="var(--accent-amber)" />
            <MetricCard icon="📊" value={data.data_points?.length || 0} label="Data Points" accentColor="var(--accent-blue)" />
            <MetricCard
              icon="📈"
              value={data.current_trend === 'spike_detected' ? 'SPIKE' : 'Stable'}
              label="Current Trend"
              accentColor={data.current_trend === 'spike_detected' ? 'var(--accent-red)' : 'var(--accent-green)'}
            />
          </div>

          <div className="glass-card mb-3 no-hover">
            <div className="section-header">
              <div className="section-title">Spread Timeline</div>
              {data.current_trend === 'spike_detected' && (
                <span className="badge badge-high" style={{ animation: 'pulse-badge 2s infinite' }}>
                  ⚠️ SPIKE — Possible coordinated push
                </span>
              )}
            </div>
            {loading ? (
              <div className="loading-spinner"><div className="spinner"></div></div>
            ) : (
              renderChart()
            )}
          </div>

          {data.anomalies && data.anomalies.length > 0 && (
            <div className="glass-card" style={{ borderColor: 'var(--border-danger)' }}>
              <div className="section-title mb-3">⚠️ Anomaly Events</div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Platform</th>
                    <th>Volume</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.anomalies.slice(0, 10).map((a, i) => (
                    <tr key={i}>
                      <td className="text-mono">{new Date(a.timestamp).toLocaleString()}</td>
                      <td>{a.platform}</td>
                      <td className="text-mono" style={{ color: 'var(--text-danger)', fontWeight: 600 }}>{a.count}</td>
                      <td><span className="badge badge-high">Anomaly</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {!data && !loading && (
        <div className="empty-state">
          <div className="empty-icon">⏱️</div>
          <div className="empty-title">No Live Data Available</div>
          <div className="empty-text">
            Run a Narrative Hunt first to analyze real timestamps, or click below to run a simulation.
          </div>
          <button className="btn btn-ghost mt-3" style={{ border: '1px solid var(--accent-blue)' }} onClick={runMockAnalysis}>
            [ SIMULATE SPREAD VELOCITY ]
          </button>
        </div>
      )}

      {loading && (
        <div className="glass-card mb-5">
          <div className="flex items-center gap-3">
            <span className="spinner" style={{ borderColor: 'var(--accent-blue)', borderTopColor: 'transparent' }}></span>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>[ SYSTEM ] Calculating Temporal Spread...</div>
              <div className="text-xs" style={{ color: 'var(--accent-cyan)' }}>Aggregating timestamp metadata and calculating delta-T vectors...</div>
            </div>
          </div>
          <div className="progress-bar mt-3" style={{ background: 'rgba(0,0,0,0.5)' }}>
            <div className="progress-fill" style={{ width: '90%', background: 'var(--accent-blue)', boxShadow: 'var(--shadow-glow-blue)' }}></div>
          </div>
        </div>
      )}
    </div>
  );
}
