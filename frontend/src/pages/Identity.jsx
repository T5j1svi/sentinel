import { useState } from 'react';
import MetricCard from '../components/MetricCard';
import api from '../api/sentinel';

export default function Identity() {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [profileData, setProfileData] = useState(null);

  const runProfile = async () => {
    if (!username.trim()) return;
    setLoading(true);
    try {
      // Use hunt API with username as narrative for cross-platform search
      const data = await api.runHunt({
        narrative: username.trim(),
        platforms: ['X', 'Telegram', 'YouTube', 'Instagram', 'TikTok', 'LinkedIn', 'Facebook'],
        depth: 6,
        fetch_metadata: true,
        fast_mode: true,
        timeout_seconds: 90,
      });
      setProfileData(data);
    } catch (err) {
      console.error('Profile error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-enter">
      <div className="glass-card mb-5">
        <div className="section-header">
          <div>
            <div className="section-title">👤 Identity Profiler</div>
            <div className="section-subtitle">
              Cross-platform account lookup, behavior analysis, and coordination detection.
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="glass-card mb-5 no-hover">
        <div className="section-subtitle mb-2">Username or Handle</div>
        <div className="flex items-center gap-3">
          <div className="search-bar" style={{ flex: 1 }}>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username, handle, or real name... e.g., @KashmirDigital"
              onKeyDown={(e) => e.key === 'Enter' && runProfile()}
            />
          </div>
          <button className="btn btn-primary" onClick={runProfile} disabled={loading || !username.trim()}>
            {loading ? (
              <>
                <span className="spinner" style={{ width: '14px', height: '14px', borderWidth: '2px' }}></span>
                Profiling...
              </>
            ) : (
              '👤 Profile'
            )}
          </button>
        </div>
      </div>

      {loading && (
        <div className="glass-card mb-3">
          <div className="flex items-center gap-3">
            <span className="spinner"></span>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600 }}>Searching across 7 platforms...</div>
              <div className="text-xs text-muted">Looking for "{username}" across social media and news platforms.</div>
            </div>
          </div>
          <div className="progress-bar mt-3">
            <div className="progress-fill" style={{ width: '50%' }}></div>
          </div>
        </div>
      )}

      {profileData && (
        <>
          <div className="metrics-grid">
            <MetricCard icon="📡" value={profileData.total_results} label="Mentions Found" accentColor="var(--accent-blue)" />
            <MetricCard icon="🌐" value={profileData.platforms_searched} label="Platforms Searched" accentColor="var(--accent-purple)" />
            <MetricCard icon="🔴" value={profileData.high_confidence} label="High Confidence" accentColor="var(--accent-red)" />
            <MetricCard icon="⚡" value={`${profileData.search_time_seconds}s`} label="Search Time" accentColor="var(--accent-green)" />
          </div>

          <div className="glass-card no-hover">
            <div className="section-header">
              <div>
                <div className="section-title">Profile Results</div>
                <div className="section-subtitle">
                  {profileData.total_results} mentions across {profileData.platforms_searched} platforms
                </div>
              </div>
            </div>

            {profileData.results?.length > 0 ? (
              <div>
                {profileData.results.map((r, i) => (
                  <div key={i} className="result-card" style={{ marginBottom: '6px' }}>
                    <div className="result-header">
                      <div className="flex items-center gap-2">
                        <span className="badge badge-platform">{r.platform}</span>
                        {r.confidence && (
                          <span className={`badge ${r.confidence === 'High' ? 'badge-high' : 'badge-medium'}`}>
                            {r.confidence}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="result-title">{r.title || 'Untitled'}</div>
                    <div className="result-snippet">{(r.snippet || '').slice(0, 200)}</div>
                    {r.url && (
                      <a href={r.url} target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm" style={{ marginTop: '4px' }}>
                        🌐 Open
                      </a>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">🔍</div>
                <div className="empty-title">No Mentions Found</div>
                <div className="empty-text">Try a different username or handle.</div>
              </div>
            )}
          </div>
        </>
      )}

      {!profileData && !loading && (
        <div className="empty-state">
          <div className="empty-icon">👤</div>
          <div className="empty-title">Ready to Profile</div>
          <div className="empty-text">
            Enter a username, handle, or real name above. SENTINEL will search across all major platforms
            and aggregate the results into a unified profile.
          </div>
        </div>
      )}
    </div>
  );
}
