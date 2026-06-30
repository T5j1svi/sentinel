import { useState, useEffect } from 'react';
import { useApp } from '../AppContext';
import MetricCard from '../components/MetricCard';
import api from '../api/sentinel';

export default function Geo() {
  const { huntResults, automatedData } = useApp();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Sync with automated background pipeline
  useEffect(() => {
    if (automatedData?.geo) {
      setData(automatedData.geo);
    }
  }, [automatedData?.geo]);

  const runMockAnalysis = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setData({
        points: [],
        total_points: 124,
        countries: {
          'Russia': 45,
          'China': 32,
          'Iran': 15,
          'United States': 32
        },
        anomalies: [
          { anomaly_reason: 'IP Geolocation mismatch with declared Profile Region', country: 'Russia', source_type: 'X (Twitter)' },
          { anomaly_reason: 'Timezone / Posting hour anomaly (UTC+3 offset)', country: 'China', source_type: 'Telegram' }
        ]
      });
    }, 2000);
  };

  // Fallback auto-run
  useEffect(() => {
    if (huntResults?.results?.length > 0 && !data && !automatedData?.geo && !loading) {
      runAnalysis();
    }
  }, [huntResults]);

  const runAnalysis = async () => {
    if (!huntResults?.results?.length) return;
    setLoading(true);
    try {
      const result = await api.analyzeGeo(huntResults.results);
      setData(result);
    } catch (err) {
      console.error('Geo analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const hasResults = huntResults?.results?.length > 0;
  const points = data?.points || [];
  const anomalies = data?.anomalies || [];
  const countries = data?.countries || {};
  const countryEntries = Object.entries(countries).sort((a, b) => b[1] - a[1]);
  const maxCount = Math.max(...Object.values(countries).map(Number), 1);
  const totalSources = data?.total_points || 0;

  // Country colors
  const countryColors = {
    Pakistan: '#16A34A', China: '#DC2626', India: '#f59e0b',
    Bangladesh: '#059669', 'United Kingdom': '#3b82f6', 'United States': '#8b5cf6',
    Russia: '#ef4444', Turkey: '#f97316', Iran: '#a855f7',
    Germany: '#6366f1', France: '#ec4899', Japan: '#06b6d4',
  };

  // Country coords for map
  const countryCoords = {
    Pakistan: { lat: 30.37, lng: 69.34 }, India: { lat: 20.59, lng: 78.96 },
    China: { lat: 35.86, lng: 104.19 }, Bangladesh: { lat: 23.68, lng: 90.35 },
    'United States': { lat: 37.09, lng: -95.71 }, 'United Kingdom': { lat: 55.37, lng: -3.43 },
    Russia: { lat: 61.52, lng: 105.31 }, Turkey: { lat: 38.96, lng: 35.24 },
    Germany: { lat: 51.16, lng: 10.45 }, Netherlands: { lat: 52.13, lng: 5.29 },
  };

  return (
    <div className="page-enter">
      <div className="glass-card mb-5">
        <div className="section-header">
          <div>
            <div className="section-title">🌍 Geo Intelligence</div>
            <div className="section-subtitle">
              Maps content origins, infrastructure locations, and identifies geographic anomalies.
            </div>
          </div>
          {hasResults && (
            <button className="btn btn-primary btn-sm" onClick={runAnalysis} disabled={loading}>
              {loading ? 'Analyzing...' : '🔄 Reanalyze'}
            </button>
          )}
        </div>
      </div>

      {!hasResults && !loading && !data && (
        <div className="empty-state">
          <div className="empty-icon">🌍</div>
          <div className="empty-title">No Live Data Available</div>
          <div className="empty-text">
            Run a Narrative Hunt first to map real results, or click below to run a simulation.
          </div>
          <button className="btn btn-ghost mt-3" style={{ border: '1px solid var(--accent-cyan)' }} onClick={runMockAnalysis}>
            [ SIMULATE GEO-TRACE ]
          </button>
        </div>
      )}

      {loading && (
        <div className="glass-card mb-5">
          <div className="flex items-center gap-3">
            <span className="spinner" style={{ borderColor: 'var(--accent-cyan)', borderTopColor: 'transparent' }}></span>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>[ SYSTEM ] Triangulating Nodes...</div>
              <div className="text-xs" style={{ color: 'var(--accent-blue)' }}>Running IP extraction and satellite overlay...</div>
            </div>
          </div>
          <div className="progress-bar mt-3" style={{ background: 'rgba(0,0,0,0.5)' }}>
            <div className="progress-fill" style={{ width: '85%', background: 'var(--accent-cyan)', boxShadow: 'var(--shadow-glow-blue)' }}></div>
          </div>
        </div>
      )}

      {data && (
        <>
          <div className="metrics-grid">
            <MetricCard icon="🌐" value={countryEntries.length} label="Countries" accentColor="var(--accent-blue)" />
            <MetricCard icon="⚠️" value={anomalies.length} label="Geo Anomalies" accentColor="var(--accent-red)" />
            <MetricCard icon="📡" value={totalSources} label="Total Sources" accentColor="var(--accent-purple)" />
            <MetricCard icon="🏗️" value={Object.keys(countries).length} label="Origins Mapped" accentColor="var(--accent-amber)" />
          </div>

          <div className="grid-2" style={{ gridTemplateColumns: '2fr 1fr' }}>
            {/* Map */}
            <div className="map-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <svg width="100%" height="100%" viewBox="0 0 800 400" style={{ background: 'transparent' }}>
                <rect x="50" y="30" width="700" height="340" fill="none" stroke="var(--border-subtle)" strokeWidth="0.5" rx="4" />
                {[100, 200, 300, 400, 500, 600, 700].map(x => (
                  <line key={`v${x}`} x1={x} y1="30" x2={x} y2="370" stroke="var(--border-subtle)" strokeWidth="0.3" strokeDasharray="4,4" />
                ))}
                {[100, 170, 240, 310].map(y => (
                  <line key={`h${y}`} x1="50" y1={y} x2="750" y2={y} stroke="var(--border-subtle)" strokeWidth="0.3" strokeDasharray="4,4" />
                ))}

                {countryEntries.map(([country, count], i) => {
                  const coords = countryCoords[country];
                  if (!coords) return null;
                  const x = 400 + (coords.lng / 180) * 350;
                  const y = 200 - (coords.lat / 90) * 170;
                  const radius = 6 + (count / maxCount) * 18;
                  const color = countryColors[country] || '#3b82f6';
                  const isAnomaly = anomalies.some(a => (a.country || '').includes(country));

                  return (
                    <g key={i}>
                      {isAnomaly && (
                        <circle cx={x} cy={y} r={radius + 8} fill="none" stroke={color} strokeWidth="1" opacity="0.3">
                          <animate attributeName="r" from={radius + 4} to={radius + 16} dur="2s" repeatCount="indefinite" />
                          <animate attributeName="opacity" from="0.4" to="0" dur="2s" repeatCount="indefinite" />
                        </circle>
                      )}
                      <circle cx={x} cy={y} r={radius} fill={color} opacity={0.15} />
                      <circle cx={x} cy={y} r={radius * 0.5} fill={color} stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
                      <text x={x} y={y + radius + 12} textAnchor="middle" fill="var(--text-secondary)" fontSize="9" fontFamily="Inter">
                        {country}
                      </text>
                      <text x={x} y={y + 3} textAnchor="middle" fill="white" fontSize="9" fontWeight="600" fontFamily="JetBrains Mono">
                        {count}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* Country breakdown */}
            <div className="glass-card">
              <div className="section-title mb-3">Source Distribution</div>
              {countryEntries.map(([country, count], i) => {
                const color = countryColors[country] || '#3b82f6';
                return (
                  <div key={i} style={{
                    padding: '8px 10px', marginBottom: '5px',
                    background: 'var(--bg-card)', border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                  }}>
                    <div className="flex items-center justify-between">
                      <span style={{ fontWeight: 600, fontSize: '12px' }}>{country}</span>
                      <span className="text-mono" style={{ fontWeight: 700, color }}>{count}</span>
                    </div>
                    <div style={{ marginTop: '4px', height: '3px', background: 'var(--bg-glass)', borderRadius: '2px', overflow: 'hidden' }}>
                      <div style={{ width: `${(count / maxCount) * 100}%`, height: '100%', background: color, borderRadius: '2px' }} />
                    </div>
                  </div>
                );
              })}
              {countryEntries.length === 0 && (
                <div className="text-xs text-muted">No geographic data extracted yet.</div>
              )}
            </div>
          </div>

          {/* Anomalies */}
          {anomalies.length > 0 && (
            <div className="glass-card mt-3" style={{ borderColor: 'var(--border-danger)' }}>
              <div className="section-title mb-3">⚠️ Geographic Anomalies</div>
              {anomalies.map((a, i) => (
                <div key={i} className="alert-card alert-danger mb-2">
                  <span style={{ fontSize: '16px' }}>⚠️</span>
                  <div>
                    <div style={{ fontWeight: 600, color: 'var(--text-danger)', fontSize: '12px' }}>
                      {a.label || a.anomaly_reason || 'Geographic mismatch detected'}
                    </div>
                    <div className="text-xs text-muted mt-1">
                      Country: {a.country || '—'} | Source: {a.source_type || '—'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
