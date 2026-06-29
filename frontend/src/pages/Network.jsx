import { useState, useEffect } from 'react';
import { useApp } from '../AppContext';
import MetricCard from '../components/MetricCard';
import api from '../api/sentinel';

export default function Network() {
  const { huntResults, huntNarrative, automatedData } = useApp();
  const [networkData, setNetworkData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);

  // Sync with automated background pipeline
  useEffect(() => {
    if (automatedData?.network) {
      setNetworkData(automatedData.network);
    }
  }, [automatedData?.network]);

  // Fallback auto-run
  useEffect(() => {
    if (huntResults?.results?.length > 0 && !networkData && !automatedData?.network && !loading) {
      buildNetwork();
    }
  }, [huntResults]);

  const buildNetwork = async () => {
    if (!huntResults?.results?.length) return;
    setLoading(true);
    try {
      const data = await api.buildNetwork(huntResults.results, huntNarrative || 'Narrative');
      setNetworkData(data);
    } catch (err) {
      console.error('Network build error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderGraph = () => {
    if (!networkData || !networkData.nodes?.length) return null;
    return (
      <iframe 
        src={`/exports/network.html?t=${Date.now()}`} 
        width="100%" 
        height="600px" 
        style={{ border: 'none', borderRadius: 'var(--radius-lg)' }} 
        title="PyVis Influence Network" 
      />
    );
  };

  const hasResults = huntResults?.results?.length > 0;

  return (
    <div className="page-enter">
      <div className="glass-card mb-5">
        <div className="section-header">
          <div>
            <div className="section-title">🕸️ Network Mapper</div>
            <div className="section-subtitle">
              Interactive influence network. Sources → Amplifiers → Bot clusters. Click nodes to inspect.
            </div>
          </div>
          <div className="flex gap-2">
            {hasResults && (
              <button className="btn btn-primary btn-sm" onClick={buildNetwork} disabled={loading}>
                {loading ? 'Building...' : '🔄 Rebuild'}
              </button>
            )}
            <button className="btn btn-ghost btn-sm">Export Gephi</button>
          </div>
        </div>
      </div>

      {!hasResults && !loading && (
        <div className="empty-state">
          <div className="empty-icon">🕸️</div>
          <div className="empty-title">No Data Available</div>
          <div className="empty-text">
            Run a Narrative Hunt first to generate the influence network.
            The network is built from real search results — no demo data.
          </div>
        </div>
      )}

      {loading && (
        <div className="loading-spinner"><div className="spinner"></div></div>
      )}

      {networkData && (
        <>
          <div className="metrics-grid">
            <MetricCard icon="🔵" value={networkData.nodes?.length || 0} label="Nodes" accentColor="var(--accent-blue)" />
            <MetricCard icon="🔗" value={networkData.edges?.length || 0} label="Edges" accentColor="var(--accent-purple)" />
            <MetricCard icon="🏘️" value={networkData.communities || 0} label="Communities" accentColor="var(--accent-amber)" />
            <MetricCard icon="🌉" value={networkData.bridge_nodes || 0} label="Bridge Nodes" accentColor="var(--accent-green)" />
          </div>

          <div className="grid-2" style={{ gridTemplateColumns: '3fr 1fr' }}>
            <div className="network-container" style={{ position: 'relative' }}>
              {renderGraph()}
            </div>

            <div className="glass-card">
              <div className="section-title mb-3">Node Inspector</div>
              {selectedNode ? (
                <div className="animate-fade-in">
                  <div style={{ fontSize: '14px', fontWeight: 700, marginBottom: '10px', color: selectedNode.color || 'var(--text-accent)' }}>
                    {selectedNode.label}
                  </div>
                  <div className="flex flex-col gap-2">
                    <div><span className="text-xs text-muted">Type:</span> <span className="text-sm">{selectedNode.node_type}</span></div>
                    <div><span className="text-xs text-muted">Platform:</span> <span className="text-sm">{selectedNode.platform || '—'}</span></div>
                    <div><span className="text-xs text-muted">Role:</span> <span className="text-sm">{selectedNode.role || '—'}</span></div>
                    <div><span className="text-xs text-muted">Confidence:</span> <span className="text-sm">{selectedNode.confidence || '—'}</span></div>
                    {selectedNode.url && (
                      <a href={selectedNode.url} target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm" style={{ alignSelf: 'flex-start' }}>
                        🌐 Open
                      </a>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-xs text-muted">Click a node in the graph to inspect its properties and connections.</div>
              )}

              {networkData.hub_nodes?.length > 0 && (
                <div style={{ marginTop: '16px' }}>
                  <div className="section-subtitle mb-2">Top Hub Nodes</div>
                  {networkData.hub_nodes.slice(0, 5).map((h, i) => (
                    <div key={i} style={{
                      padding: '6px 8px', background: 'var(--bg-card)',
                      border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)',
                      marginBottom: '3px', fontSize: '11px', fontWeight: 500,
                    }}>
                      {String(h).slice(0, 40)}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
