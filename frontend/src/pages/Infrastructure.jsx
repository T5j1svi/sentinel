import { useState, useEffect } from 'react';
import { useApp } from '../AppContext';
import MetricCard from '../components/MetricCard';
import api from '../api/sentinel';

export default function Infrastructure() {
  const { huntResults, automatedData } = useApp();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Sync with automated background pipeline
  useEffect(() => {
    if (automatedData?.infrastructure) {
      setData(automatedData.infrastructure);
    }
  }, [automatedData?.infrastructure]);

  // Fallback auto-run
  useEffect(() => {
    if (huntResults?.results?.length > 0 && !data && !automatedData?.infrastructure && !loading) {
      runAnalysis();
    }
  }, [huntResults]);

  const runAnalysis = async () => {
    if (!huntResults?.results?.length) return;
    setLoading(true);
    try {
      const result = await api.analyzeInfrastructure(huntResults.results);
      setData(result);
    } catch (err) {
      console.error('Infrastructure analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const hasResults = huntResults?.results?.length > 0;
  const domains = data?.domains || [];
  const sharedClusters = data?.shared_infrastructure_clusters || 0;
  const privacyShields = domains.filter(d => d.privacy_shield).length;
  const hostingCountries = [...new Set(domains.map(d => d.hosting_country).filter(Boolean))].length;

  return (
    <div className="page-enter">
      <div className="glass-card mb-5">
        <div className="section-header">
          <div>
            <div className="section-title">🏗️ Infrastructure OSINT</div>
            <div className="section-subtitle">
              WHOIS, DNS, certificate transparency, and hosting analysis. Discovers shared infrastructure clusters.
            </div>
          </div>
          {hasResults && (
            <button className="btn btn-primary" onClick={runAnalysis} disabled={loading}>
              {loading ? 'Analyzing...' : '🔍 Analyze Domains'}
            </button>
          )}
        </div>
      </div>

      {!hasResults && !loading && (
        <div className="empty-state">
          <div className="empty-icon">🏗️</div>
          <div className="empty-title">No Data Available</div>
          <div className="empty-text">
            Run a Narrative Hunt first. Infrastructure analysis extracts domains from real search results.
          </div>
        </div>
      )}

      {loading && (
        <div className="loading-spinner"><div className="spinner"></div></div>
      )}

      {data && (
        <>
          <div className="metrics-grid">
            <MetricCard icon="🌐" value={data.domains_analyzed || domains.length} label="Domains Analyzed" accentColor="var(--accent-blue)" />
            <MetricCard icon="🔗" value={sharedClusters} label="Shared Infra Clusters" accentColor="var(--accent-red)" />
            <MetricCard icon="🛡️" value={privacyShields} label="Privacy Shields" accentColor="var(--accent-amber)" />
            <MetricCard icon="🌏" value={hostingCountries} label="Hosting Countries" accentColor="var(--accent-purple)" />
          </div>

          {/* Shared infrastructure alert */}
          {sharedClusters > 0 && (
            <div className="alert-card alert-danger mb-3">
              <span style={{ fontSize: '20px' }}>⚠️</span>
              <div>
                <div style={{ fontWeight: 700, color: 'var(--text-danger)', fontSize: '13px' }}>Shared Infrastructure Detected</div>
                <div className="text-xs" style={{ color: 'var(--text-danger)', opacity: 0.8 }}>
                  {sharedClusters} cluster(s) of domains sharing the same hosting infrastructure detected.
                </div>
              </div>
            </div>
          )}

          {/* Domain table */}
          {domains.length > 0 && (
            <div className="glass-card no-hover">
              <div className="section-title mb-3">Domain Intelligence</div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Domain</th>
                    <th>Registrar</th>
                    <th>Country</th>
                    <th>Registered</th>
                    <th>Hosting</th>
                    <th>IP</th>
                    <th>ASN</th>
                    <th>Privacy</th>
                  </tr>
                </thead>
                <tbody>
                  {domains.map((d, i) => {
                      const isShared = false; // clusters detail not exposed by API
                    return (
                      <tr key={i} style={isShared ? { background: 'var(--accent-red-glow)' } : {}}>
                        <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{d.domain}</td>
                        <td>{d.registrar || '—'}</td>
                        <td>{d.registrant_country || '—'}</td>
                        <td className="text-mono">{d.registration_date || '—'}</td>
                        <td>{d.hosting_country || '—'}</td>
                        <td className="text-mono" style={{ fontSize: '10px' }}>{d.ip_address || '—'}</td>
                        <td className="text-xs">{d.asn || '—'}</td>
                        <td>
                          {d.privacy_shield ? (
                            <span className="badge badge-medium">🛡️ Shield</span>
                          ) : (
                            <span className="badge badge-low">None</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {domains.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">🌐</div>
              <div className="empty-title">No Domains Found</div>
              <div className="empty-text">No extractable domains in the current hunt results.</div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
