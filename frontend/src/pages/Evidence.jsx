import { useState, useEffect } from 'react';
import { useApp } from '../AppContext';
import MetricCard from '../components/MetricCard';
import api from '../api/sentinel';

export default function Evidence() {
  const { caseId, setEvidenceCount } = useApp();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchFilter, setSearchFilter] = useState('');

  useEffect(() => {
    loadEvidence();
  }, [caseId]);

  const loadEvidence = async () => {
    setLoading(true);
    try {
      const data = await api.getEvidence(caseId || 'default');
      const evidenceItems = data?.items || data?.evidence || [];
      setItems(Array.isArray(evidenceItems) ? evidenceItems : []);
      setEvidenceCount(Array.isArray(evidenceItems) ? evidenceItems.length : 0);
    } catch (err) {
      console.error('Evidence load error:', err);
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  const copyHash = (hash) => {
    navigator.clipboard.writeText(hash).catch(() => {});
  };

  const filtered = items.filter(e =>
    !searchFilter ||
    (e.title || '').toLowerCase().includes(searchFilter.toLowerCase()) ||
    (e.platform || '').toLowerCase().includes(searchFilter.toLowerCase())
  );

  const lockedCount = items.filter(e => e.locked).length;
  const archivedCount = items.filter(e => e.archive_url).length;
  const platforms = [...new Set(items.map(e => e.platform).filter(Boolean))];

  return (
    <div className="page-enter">
      <div className="glass-card mb-5">
        <div className="section-header">
          <div>
            <div className="section-title">🔒 Evidence Locker</div>
            <div className="section-subtitle">
              Cryptographically secured evidence with SHA-256 hashing, Wayback archiving, and chain of custody.
            </div>
          </div>
          <div className="flex gap-2">
            <button className="btn btn-ghost btn-sm" onClick={loadEvidence}>🔄 Refresh</button>
            <button className="btn btn-ghost btn-sm">📦 Export ZIP</button>
          </div>
        </div>
      </div>

      <div className="metrics-grid">
        <MetricCard icon="🔒" value={lockedCount} label="Locked Items" accentColor="var(--accent-green)" />
        <MetricCard icon="📎" value={archivedCount} label="Archived" accentColor="var(--accent-blue)" />
        <MetricCard icon="📡" value={platforms.length} label="Platforms" accentColor="var(--accent-purple)" />
        <MetricCard icon="#️⃣" value="SHA-256" label="Hash Algorithm" accentColor="var(--accent-amber)" />
      </div>

      {/* Search */}
      <div className="search-bar mb-3">
        <input
          type="text"
          value={searchFilter}
          onChange={(e) => setSearchFilter(e.target.value)}
          placeholder="Filter evidence by title, platform..."
        />
      </div>

      {loading && (
        <div className="loading-spinner"><div className="spinner"></div></div>
      )}

      {!loading && items.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🔒</div>
          <div className="empty-title">Evidence Locker Empty</div>
          <div className="empty-text">
            Lock evidence from hunt results using the 🔒 Lock button on result cards. Each locked item gets a SHA-256 hash and timestamp.
          </div>
        </div>
      )}

      {!loading && filtered.length > 0 && (
        <div className="flex flex-col gap-2">
          {filtered.map((item, i) => (
            <div key={item.evidence_id || i} className="evidence-item animate-slide-up" style={{ animationDelay: `${i * 0.04}s` }}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="badge badge-platform">{item.platform || 'Unknown'}</span>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {item.title || 'Untitled evidence'}
                  </span>
                </div>
                {item.locked && (
                  <div className="evidence-locked">🔒 LOCKED</div>
                )}
              </div>

              <div className="grid-3" style={{ gridTemplateColumns: '1fr 2fr 1fr' }}>
                <div>
                  <div className="text-xs text-muted mb-1">Evidence ID</div>
                  <div className="text-mono" style={{ fontSize: '12px', color: 'var(--text-accent)' }}>
                    {(item.evidence_id || '').slice(0, 8)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-muted mb-1">SHA-256 Content Hash</div>
                  <div className="evidence-hash">{item.content_hash || '—'}</div>
                </div>
                <div>
                  <div className="text-xs text-muted mb-1">Collected At</div>
                  <div className="text-mono text-xs">
                    {item.collected_at ? new Date(item.collected_at).toLocaleString() : '—'}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 mt-2">
                {item.source_url && (
                  <a href={item.source_url} target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm">
                    🌐 Source
                  </a>
                )}
                {item.archive_url && (
                  <a href={item.archive_url} target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm">
                    📎 Archive
                  </a>
                )}
                {item.content_hash && (
                  <button className="btn btn-ghost btn-sm" onClick={() => copyHash(item.content_hash)}>
                    📋 Copy Hash
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
