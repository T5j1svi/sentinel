import { useState, useEffect } from 'react';
import { useApp } from '../AppContext';
import MetricCard from '../components/MetricCard';
import api from '../api/sentinel';

export default function Tactics() {
  const { huntResults, automatedData } = useApp();
  const [taxonomy, setTaxonomy] = useState([]);
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedTactic, setSelectedTactic] = useState(null);

  // Load taxonomy on mount
  useEffect(() => {
    const loadTaxonomy = async () => {
      try {
        const data = await api.getTaxonomy();
        if (data?.tactics) setTaxonomy(data.tactics);
      } catch (err) {
        console.error('Taxonomy load error:', err);
      }
    };
    loadTaxonomy();
  }, []);

  // Sync with automated background pipeline
  useEffect(() => {
    if (automatedData?.tactics) {
      setAnalysisData(automatedData.tactics);
    }
  }, [automatedData?.tactics]);

  // Fallback auto-run
  useEffect(() => {
    if (huntResults?.results?.length > 0 && !analysisData && !automatedData?.tactics && !loading) {
      runAnalysis();
    }
  }, [huntResults]);

  const runAnalysis = async () => {
    if (!huntResults?.results?.length) return;
    setLoading(true);
    try {
      const data = await api.analyzeTactics(huntResults.results);
      setAnalysisData(data);
    } catch (err) {
      console.error('Tactics analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Merge taxonomy with analysis counts
  const tactics = taxonomy.length > 0 ? taxonomy : [
    { tactic_id: 'T0001', name: 'False Context', description: 'Real content placed in false framing', signal: 'Verifiable fact contradiction' },
    { tactic_id: 'T0002', name: 'Fabricated Content', description: 'Entirely made-up stories', signal: 'No primary source found' },
    { tactic_id: 'T0003', name: 'Impersonation', description: 'Fake account mimicking real entity', signal: 'Username/avatar similarity' },
    { tactic_id: 'T0004', name: 'Astroturfing', description: 'Fake grassroots appearance', signal: 'Coordination score > 70' },
    { tactic_id: 'T0005', name: 'State-Sponsored', description: 'Government-linked amplification', signal: 'Infrastructure attribution' },
    { tactic_id: 'T0006', name: 'Emotional Manipulation', description: 'Fear/anger/outrage appeals', signal: 'Extreme sentiment polarity' },
    { tactic_id: 'T0007', name: 'Conspiracy Narrative', description: 'Unverified hidden-hand claims', signal: 'Claims without evidence' },
    { tactic_id: 'T0008', name: 'Hack-and-Leak', description: 'Distribution of stolen materials', signal: 'Unverified document drops' },
  ];

  // Get counts from analysis data
  const getCounts = (tacticName) => {
    if (!analysisData?.tactic_distribution) return 0;
    return analysisData.tactic_distribution[tacticName] || 0;
  };

  const tacticItems = tactics.map(t => ({
    ...t,
    id: t.tactic_id || t.id,
    count: getCounts(t.name),
  }));

  const maxCount = Math.max(...tacticItems.map(t => t.count), 1);
  const totalClassified = analysisData?.total_classified || tacticItems.reduce((sum, t) => sum + t.count, 0);
  const hasResults = huntResults?.results?.length > 0;

  return (
    <div className="page-enter">
      <div className="glass-card mb-5">
        <div className="section-header">
          <div>
            <div className="section-title">🛡️ DISARM Tactic Classifier</div>
            <div className="section-subtitle">
              Auto-classifies content against the DISARM Framework — the MITRE ATT&CK equivalent for information operations.
            </div>
          </div>
          {hasResults && (
            <button className="btn btn-primary" onClick={runAnalysis} disabled={loading}>
              {loading ? 'Classifying...' : '🔍 Classify Results'}
            </button>
          )}
        </div>
      </div>

      {!hasResults && (
        <div className="empty-state">
          <div className="empty-icon">🛡️</div>
          <div className="empty-title">No Data to Classify</div>
          <div className="empty-text">
            Run a Narrative Hunt first. DISARM classification requires real content from search results.
          </div>
        </div>
      )}

      {loading && (
        <div className="loading-spinner"><div className="spinner"></div></div>
      )}

      {(hasResults || totalClassified > 0) && !loading && (
        <>
          <div className="metrics-grid">
            <MetricCard icon="📊" value={totalClassified} label="Content Classified" accentColor="var(--accent-blue)" />
            <MetricCard icon="🔴" value={getCounts('Emotional Manipulation')} label="Emotional Manipulation" accentColor="var(--accent-red)" />
            <MetricCard icon="⚠️" value={getCounts('False Context')} label="False Context" accentColor="var(--accent-amber)" />
            <MetricCard icon="🤖" value={getCounts('Astroturfing')} label="Astroturfing" accentColor="var(--accent-purple)" />
          </div>

          {/* DISARM Matrix Heatmap */}
          <div className="glass-card mb-3 no-hover">
            <div className="section-title mb-3">DISARM Matrix Heatmap</div>
            <div className="disarm-matrix">
              {tacticItems.map(tactic => {
                const intensity = maxCount > 0 ? tactic.count / maxCount : 0;
                const isHot = intensity > 0.6;
                return (
                  <div
                    key={tactic.id}
                    className={`disarm-cell ${isHot ? 'hot' : ''}`}
                    onClick={() => setSelectedTactic(tactic)}
                    style={{
                      cursor: 'pointer',
                      background: isHot
                        ? `rgba(239,68,68,${intensity * 0.12})`
                        : `rgba(59,130,246,${Math.max(intensity * 0.06, 0.02)})`,
                    }}
                  >
                    <div className="cell-id">{tactic.id}</div>
                    <div className="cell-name">{tactic.name}</div>
                    <div className="cell-count">{tactic.count}</div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Detail */}
          <div className="grid-2">
            <div className="glass-card no-hover">
              <div className="section-title mb-3">Tactic Taxonomy</div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Tactic</th>
                    <th>Description</th>
                    <th>Signal</th>
                    <th>Count</th>
                  </tr>
                </thead>
                <tbody>
                  {tacticItems.map(t => (
                    <tr key={t.id} onClick={() => setSelectedTactic(t)} style={{ cursor: 'pointer' }}>
                      <td className="text-mono" style={{ color: 'var(--text-accent)' }}>{t.id}</td>
                      <td style={{ fontWeight: 600 }}>{t.name}</td>
                      <td>{t.description}</td>
                      <td className="text-xs text-muted">{t.signal}</td>
                      <td>
                        <span className={`badge ${t.count > 10 ? 'badge-high' : t.count > 5 ? 'badge-medium' : 'badge-low'}`}>
                          {t.count}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="glass-card">
              <div className="section-title mb-3">
                {selectedTactic ? `${selectedTactic.id}: ${selectedTactic.name}` : 'Select a Tactic'}
              </div>
              {selectedTactic ? (
                <div className="animate-fade-in">
                  <div className="mb-3">
                    <span className="badge badge-tactic" style={{ fontSize: '11px', padding: '4px 10px' }}>
                      {selectedTactic.id}
                    </span>
                  </div>
                  <p style={{ fontSize: '13px', marginBottom: '10px' }}>{selectedTactic.description}</p>
                  <div className="mb-3">
                    <span className="text-xs text-muted">Detection signal:</span>
                    <div style={{ fontSize: '12px', marginTop: '3px' }}>{selectedTactic.signal}</div>
                  </div>
                  <div>
                    <span className="text-xs text-muted">Instances found:</span>
                    <div className="text-mono" style={{ fontSize: '22px', fontWeight: 700, color: selectedTactic.count > 10 ? 'var(--accent-red)' : 'var(--accent-blue)' }}>
                      {selectedTactic.count}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-xs text-muted">Click a tactic in the matrix or table to view details.</div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
