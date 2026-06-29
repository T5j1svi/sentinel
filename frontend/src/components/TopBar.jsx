import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useApp } from '../AppContext';
import { api } from '../api/sentinel';


const pageTitles = {
  '/': 'Command Center',
  '/hunt': 'Narrative Hunt',
  '/identity': 'Identity Profiler',
  '/media': 'Media Forensics',
  '/velocity': 'Velocity Monitor',
  '/network': 'Network Mapper',
  '/bots': 'Behaviour Profiler',
  '/tactics': 'DISARM Tactic Classifier',
  '/infrastructure': 'Infrastructure OSINT',
  '/evidence': 'Evidence Locker',
  '/geo': 'Geo Intelligence',
  '/reports': 'Report Generator',
};

export default function TopBar() {
  const location = useLocation();
  const { caseName, evidenceCount, activeTasks, threatLevel } = useApp();
  const title = pageTitles[location.pathname] || 'SENTINEL';

  const threatClass = {
    Minimal: 'threat-minimal',
    Low: 'threat-low',
    Medium: 'threat-medium',
    High: 'threat-high',
    Critical: 'threat-critical',
  }[threatLevel] || 'threat-minimal';

  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await api.systemStatus();
        setSystemStatus(status);
      } catch (err) {
        console.error("Failed to fetch system status", err);
      }
    };
    
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const now = new Date().toLocaleString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
  });


  return (
    <header className="topbar">
      <div className="topbar-left" style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <span className="topbar-page-title">{title}</span>
        <span className="topbar-breadcrumb">SENTINEL v3.0</span>
        
        {systemStatus && (
          <div className="system-status-indicator" style={{ display: 'flex', gap: '8px', marginLeft: '20px', borderLeft: '1px solid var(--border-default)', paddingLeft: '20px' }}>
            {systemStatus.services.map(svc => (
              <span 
                key={svc.name} 
                title={`${svc.name}: ${svc.status} (${svc.latency_ms}ms)`}
                style={{
                  display: 'inline-block',
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: svc.status === 'online' ? '#10b981' : svc.status === 'degraded' ? '#f59e0b' : '#ef4444',
                  boxShadow: `0 0 5px ${svc.status === 'online' ? '#10b981' : svc.status === 'degraded' ? '#f59e0b' : '#ef4444'}`,
                  cursor: 'help'
                }}
              />
            ))}
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginLeft: '4px' }}>APIs</span>
          </div>
        )}
      </div>

      <div className="topbar-right">
        <span className="topbar-badge case-badge">
          📂 {caseName}
        </span>
        {evidenceCount > 0 && (
          <span className="topbar-badge evidence-badge">
            🔒 {evidenceCount} evidence
          </span>
        )}
        {activeTasks > 0 && (
          <span className="topbar-badge task-badge">
            ●● {activeTasks} task{activeTasks !== 1 ? 's' : ''}
          </span>
        )}
        <span className="topbar-badge" style={{ background: 'var(--bg-card)', borderColor: 'var(--border-default)', color: 'var(--text-muted)' }}>
          {now}
        </span>
        <span className={`topbar-badge ${threatClass}`}>
          {threatLevel === 'Critical' ? '🔴' : threatLevel === 'High' ? '🟠' : threatLevel === 'Medium' ? '🟡' : '🟢'}
          {threatLevel}
        </span>
      </div>
    </header>
  );
}
