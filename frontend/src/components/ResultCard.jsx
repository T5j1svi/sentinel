import { useState } from 'react';

export default function ResultCard({ result, onLockEvidence }) {
  const [expanded, setExpanded] = useState(false);

  const getSimColor = (score) => {
    if (score >= 80) return 'var(--text-success)';
    if (score >= 50) return 'var(--text-warning)';
    return 'var(--text-muted)';
  };

  const getConfidenceColor = (conf) => {
    if (conf === 'High') return 'var(--accent-red)';
    if (conf === 'Medium') return 'var(--accent-amber)';
    return 'var(--accent-blue)';
  };

  const simScore = Math.round((result.similarity_score || 0) * 100);
  const confColor = getConfidenceColor(result.confidence);

  return (
    <div className="result-card" onClick={() => setExpanded(!expanded)}>
      <div className="result-header">
        <div className="flex items-center gap-2">
          <span className="result-platform">{result.platform}</span>
          {result.language && result.language !== 'English' && (
            <span className="badge badge-language">{result.language}</span>
          )}
          {result.confidence && (
            <span className={`badge ${result.confidence === 'High' ? 'badge-high' : result.confidence === 'Medium' ? 'badge-medium' : 'badge-low'}`}>
              {result.confidence}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          {result.disarm_tags && result.disarm_tags.length > 0 && (
            <span className="badge badge-tactic">⚑ {result.disarm_tags[0]}</span>
          )}
          <span className="result-similarity" style={{ color: getSimColor(simScore) }}>
            {simScore}%
          </span>
        </div>
      </div>

      <div className="result-title">{result.title || 'Untitled'}</div>
      <div className="result-snippet">
        {result.snippet ? (expanded ? result.snippet : result.snippet.slice(0, 200) + (result.snippet.length > 200 ? '...' : '')) : 'No preview available'}
      </div>

      {/* Confidence bar */}
      <div className="confidence-bar mb-2">
        <span className="text-xs text-muted">Confidence</span>
        <div className="bar-track">
          <div className="bar-fill" style={{ width: `${simScore}%`, background: confColor }} />
        </div>
        <span className="text-mono text-xs" style={{ color: confColor }}>{simScore}%</span>
      </div>

      <div className="result-meta">
        {result.handle && (
          <span className="badge badge-platform">{result.handle}</span>
        )}
        {result.matched_terms && (
          <span className="badge badge-entity">{result.matched_term_count || 0} terms</span>
        )}
        {result.domain && (
          <span className="text-xs text-muted">{result.domain}</span>
        )}
      </div>

      {expanded && (
        <div className="result-actions animate-fade-in" onClick={(e) => e.stopPropagation()}>
          {onLockEvidence && (
            <button className="btn btn-ghost btn-sm" onClick={() => onLockEvidence(result)}>
              🔒 Lock
            </button>
          )}
          {result.url && (
            <a href={result.url} target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm">
              🌐 Open
            </a>
          )}
          <button className="btn btn-ghost btn-sm">📎 Archive</button>
          <button className="btn btn-ghost btn-sm">+ Case</button>
        </div>
      )}
    </div>
  );
}
