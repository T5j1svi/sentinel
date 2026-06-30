import { useState, useEffect } from 'react';
import { useApp } from '../AppContext';
import MetricCard from '../components/MetricCard';
import api from '../api/sentinel';

export default function Bots() {
  const { huntResults, automatedData } = useApp();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Sync with automated background pipeline
  useEffect(() => {
    if (automatedData?.bots) {
      setData(automatedData.bots);
    }
  }, [automatedData?.bots]);

  const runMockAnalysis = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setData({
        analyzed_accounts: 45,
        suspected_bots: 12,
        coordination_score: 8.4,
        bot_clusters: [
          { name: 'Cluster Alpha (Astroturf)', size: 8, confidence: 'High' },
          { name: 'Cluster Beta (Retweet Ring)', size: 4, confidence: 'Medium' }
        ]
      });
    }, 2000);
  };

  // Fallback auto-run if no automated pipeline data (e.g. legacy state)
  useEffect(() => {
    if (huntResults?.results?.length > 0 && !data && !automatedData?.bots && !loading) {
      runAnalysis();
    }
  }, [huntResults]);

  const runAnalysis = async () => {
    if (!huntResults?.results?.length) return;
    setLoading(true);
    try {
      const result = await api.analyzeBots(huntResults.results);
      setData(result);
    } catch (err) {
      console.error('Bot analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 75) return 'var(--accent-red)';
    if (score >= 45) return 'var(--accent-amber)';
    return 'var(--accent-green)';
  };

  const hasResults = huntResults?.results?.length > 0;
  const scores = data?.scores || [];
  const highRisk = scores.filter(s => s.bot_risk_score >= 75).length;
  const suspicious = scores.filter(s => s.bot_risk_score >= 45 && s.bot_risk_score < 75).length;

  return (
    <div className="page-enter">
      <div className="glass-card mb-5">
        <div className="section-header">
          <div>
            <div className="section-title">🤖 Behaviour Profiler</div>
            <div className="section-subtitle">
              Analyzes public behavioral signals to identify bots, sockpuppets, and coordinated networks.
            </div>
          </div>
          {hasResults && (
            <button className="btn btn-primary" onClick={runAnalysis} disabled={loading}>
              {loading ? 'Analyzing...' : '🔍 Run Analysis'}
            </button>
          )}
        </div>
      </div>

      {!hasResults && !loading && !data && (
        <div className="empty-state">
          <div className="empty-icon">🤖</div>
          <div className="empty-title">No Live Data Available</div>
          <div className="empty-text">
            Run a Narrative Hunt first to analyze real accounts, or click below to run a simulation.
          </div>
          <button className="btn btn-ghost mt-3" style={{ border: '1px solid var(--accent-purple)' }} onClick={runMockAnalysis}>
            [ SIMULATE BOT DETECTION ]
          </button>
        </div>
      )}

      {loading && (
        <div className="glass-card mb-5">
          <div className="flex items-center gap-3">
            <span className="spinner" style={{ borderColor: 'var(--accent-purple)', borderTopColor: 'transparent' }}></span>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>[ SYSTEM ] Analyzing Account Behaviors...</div>
              <div className="text-xs" style={{ color: 'var(--accent-blue)' }}>Running temporal correlation and text-similarity checks...</div>
            </div>
          </div>
          <div className="progress-bar mt-3" style={{ background: 'rgba(0,0,0,0.5)' }}>
            <div className="progress-fill" style={{ width: '72%', background: 'var(--accent-purple)', boxShadow: 'var(--shadow-glow-purple)' }}></div>
          </div>
        </div>
      )}

      {data && (
        <>
          <div className="metrics-grid">
            <MetricCard icon="🤖" value={data.total_analyzed} label="Accounts Analyzed" accentColor="var(--accent-blue)" />
            <MetricCard icon="🔴" value={highRisk} label="High Risk" accentColor="var(--accent-red)" />
            <MetricCard icon="🟡" value={suspicious} label="Suspicious" accentColor="var(--accent-amber)" />
            <MetricCard icon="🏘️" value={data.coordinated_clusters} label="Coordinated Clusters" accentColor="var(--accent-purple)" />
          </div>

          {scores.length > 0 ? (
            <div className="glass-card no-hover">
              <div className="section-title mb-3">Coordination & Bot Scoring</div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Handle</th>
                    <th>Platform</th>
                    <th>Risk Score</th>
                    <th>Classification</th>
                  </tr>
                </thead>
                <tbody>
                  {scores.map((score, i) => (
                    <tr key={i} className="animate-slide-up" style={{ animationDelay: `${i * 0.04}s` }}>
                      <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{score.handle}</td>
                      <td><span className="badge badge-platform">{score.platform}</span></td>
                      <td>
                        <div className="confidence-bar">
                          <div className="bar-track" style={{ width: '50px' }}>
                            <div className="bar-fill" style={{ width: `${score.bot_risk_score}%`, background: getScoreColor(score.bot_risk_score) }} />
                          </div>
                          <span className="text-mono" style={{ fontSize: '12px', fontWeight: 700, color: getScoreColor(score.bot_risk_score) }}>
                            {score.bot_risk_score}
                          </span>
                        </div>
                      </td>
                      <td>
                        <span className={`badge ${score.bot_risk_score >= 75 ? 'badge-high' : score.bot_risk_score >= 45 ? 'badge-medium' : 'badge-success'}`}>
                          {score.classification}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <div className="empty-title">No Bot Scores</div>
              <div className="empty-text">The analysis completed but no account handles were found to score.</div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
