export default function MetricCard({ icon, value, label, accentColor, trend, trendDir, className = '' }) {
  return (
    <div
      className={`metric-card animate-slide-up ${className}`}
      style={{ '--metric-accent': accentColor || 'var(--accent-blue)' }}
    >
      <div className="metric-header">
        <span className="metric-icon">{icon}</span>
        {trend && (
          <span className={`metric-trend ${trendDir === 'up' ? 'up' : trendDir === 'down' ? 'down' : ''}`}>
            {trendDir === 'up' ? '↑' : trendDir === 'down' ? '↓' : ''} {trend}
          </span>
        )}
      </div>
      <div className="metric-value" style={{ color: accentColor || 'var(--text-primary)' }}>
        {value}
      </div>
      <div className="metric-label">{label}</div>
    </div>
  );
}
