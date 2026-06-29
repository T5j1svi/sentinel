import { useState } from 'react';
import { useApp } from '../AppContext';
import api from '../api/sentinel';
import MetricCard from '../components/MetricCard';
import ResultCard from '../components/ResultCard';

const ALL_PLATFORMS = [
  'X', 'Telegram', 'YouTube', 'Facebook', 'Instagram', 'TikTok', 'LinkedIn',
  'Pakistan News', 'Kashmir / AJK News', 'China News', 'Bangladesh News',
  'Tibet News', 'Global News', 'Websites',
];

const DEFAULT_PLATFORMS = [
  'X', 'Telegram', 'YouTube', 'Pakistan News', 'Kashmir / AJK News', 'China News',
];

export default function Hunt() {
  const { storeHuntResults, incrementEvidence, setAutomatedData } = useApp();
  const [narrative, setNarrative] = useState('');
  const [platforms, setPlatforms] = useState(DEFAULT_PLATFORMS);
  const [depth, setDepth] = useState(6);
  const [fastMode, setFastMode] = useState(true);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState('');

  const togglePlatform = (p) => {
    setPlatforms(prev =>
      prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p]
    );
  };

  const runHunt = async () => {
    if (!narrative.trim()) return;
    setLoading(true);
    setError('');
    
    // Reset automated data
    setAutomatedData({
      bots: null, geo: null, tactics: null, network: null, infrastructure: null
    });

    try {
      const data = await api.runHunt({
        narrative: narrative.trim(),
        platforms,
        depth,
        fetch_metadata: true,
        fast_mode: fastMode,
        timeout_seconds: fastMode ? 90 : 240,
      });
      setResponse(data);
      // Store results in global context for other modules
      storeHuntResults(data, narrative.trim());
      
      // Real-time Automated Pipeline execution: 
      // Do not await these so UI unblocks and user can start viewing Hunt results instantly.
      if (data?.results?.length > 0) {
        Promise.allSettled([
          api.analyzeBots(data.results),
          api.analyzeGeo(data.results),
          api.analyzeTactics(data.results),
          api.buildNetwork(data.results, narrative.trim()),
          api.analyzeInfrastructure(data.results)
        ]).then((results) => {
          setAutomatedData({
            bots: results[0].status === 'fulfilled' ? results[0].value : null,
            geo: results[1].status === 'fulfilled' ? results[1].value : null,
            tactics: results[2].status === 'fulfilled' ? results[2].value : null,
            network: results[3].status === 'fulfilled' ? results[3].value : null,
            infrastructure: results[4].status === 'fulfilled' ? results[4].value : null,
          });
        });
      }
      
    } catch (err) {
      setError(err.message || 'Search failed. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const handleLockEvidence = async (result) => {
    try {
      await api.lockEvidence({
        source_url: result.url,
        content: result.snippet,
        title: result.title,
        platform: result.platform,
        case_id: 'default',
        notes: '',
      });
      incrementEvidence();
    } catch (err) {
      console.error('Failed to lock evidence:', err);
    }
  };

  return (
    <div className="page-enter">
      {/* Search Section */}
      <div className="glass-card mb-5">
        <div className="section-header">
          <div>
            <div className="section-title">🎯 Narrative Hunt</div>
            <div className="section-subtitle">
              Describe the narrative in natural language. Cross-lingual semantic search across all platforms.
            </div>
          </div>
        </div>

        <div className="search-bar mb-3">
          <textarea
            value={narrative}
            onChange={(e) => setNarrative(e.target.value)}
            placeholder="Describe the narrative to investigate... e.g., 'Indian Army General removed from command in Kashmir operation'"
            rows={3}
          />
        </div>

        {/* Platform toggles */}
        <div className="mb-3">
          <div style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '6px' }}>
            Platform Packs
          </div>
          <div className="chip-group">
            {ALL_PLATFORMS.map(p => (
              <span
                key={p}
                className={`chip ${platforms.includes(p) ? 'active' : ''}`}
                onClick={() => togglePlatform(p)}
              >
                {p}
              </span>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button
            className="btn btn-primary"
            onClick={runHunt}
            disabled={loading || !narrative.trim()}
            style={{ minWidth: '130px' }}
          >
            {loading ? (
              <>
                <span className="spinner" style={{ width: '14px', height: '14px', borderWidth: '2px' }}></span>
                Hunting...
              </>
            ) : (
              '🎯 Launch Hunt'
            )}
          </button>

          {/* Mode toggle */}
          <div className="tab-group">
            <button className={`tab-item ${fastMode ? 'active' : ''}`} onClick={() => setFastMode(true)}>
              ⚡ Fast 90s
            </button>
            <button className={`tab-item ${!fastMode ? 'active' : ''}`} onClick={() => setFastMode(false)}>
              🔍 Deep
            </button>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-muted">Depth:</span>
            <input
              type="range"
              min={3}
              max={12}
              value={depth}
              onChange={(e) => setDepth(Number(e.target.value))}
              style={{ width: '80px', accentColor: 'var(--accent-blue)' }}
            />
            <span className="text-mono text-xs" style={{ color: 'var(--text-accent)' }}>{depth}</span>
          </div>

          <span className="text-xs text-muted">
            {platforms.length} platform{platforms.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="alert-card alert-danger mb-3">
          <span>⚠️</span>
          <div style={{ fontSize: '12px', color: 'var(--text-danger)' }}>{error}</div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="glass-card mb-3">
          <div className="flex items-center gap-3">
            <span className="spinner"></span>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600 }}>Hunting across {platforms.length} platforms...</div>
              <div className="text-xs text-muted">Searching EN, UR, HI, ZH, BN translations. Results stream as platforms complete.</div>
            </div>
          </div>
          <div className="progress-bar mt-3">
            <div className="progress-fill" style={{ width: '60%' }}></div>
          </div>
        </div>
      )}

      {/* Results */}
      {response && (
        <>
          {/* Metrics */}
          <div className="metrics-grid">
            <MetricCard icon="🎯" value={response.total_results} label="Results Found" accentColor="var(--accent-blue)" />
            <MetricCard icon="📡" value={response.platforms_searched} label="Platforms Hit" accentColor="var(--accent-purple)" />
            <MetricCard icon="🔴" value={response.high_confidence} label="High Confidence" accentColor="var(--accent-red)" />
            <MetricCard icon="🖼️" value={response.media_items} label="Media Items" accentColor="var(--accent-amber)" />
            <MetricCard icon="⚡" value={`${response.search_time_seconds}s`} label="Search Time" accentColor="var(--accent-green)" />
          </div>

          {/* Result cards */}
          <div className="glass-card no-hover">
            <div className="section-header">
              <div>
                <div className="section-title">Hunt Results</div>
                <div className="section-subtitle">
                  {response.total_results} results from {response.queries_used} queries across {response.platforms_searched} platforms
                </div>
              </div>
            </div>

            {response.results.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🔍</div>
                <div className="empty-title">No results found</div>
                <div className="empty-text">Try broadening your narrative or adding more platforms.</div>
              </div>
            ) : (
              <div>
                {response.results.map((result, i) => (
                  <ResultCard
                    key={result.id || i}
                    result={result}
                    onLockEvidence={handleLockEvidence}
                  />
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* Default state */}
      {!response && !loading && (
        <div className="empty-state">
          <div className="empty-icon">🎯</div>
          <div className="empty-title">Ready to Hunt</div>
          <div className="empty-text">
            Enter a narrative description above and select your target platforms.
            SENTINEL will search across all selected platforms in 12 languages simultaneously.
          </div>
        </div>
      )}
    </div>
  );
}
