import { NavLink } from 'react-router-dom';
import { useApp } from '../AppContext';

const navItems = [
  { label: 'COMMAND', items: [
    { path: '/', icon: '⚡', label: 'Dashboard' },
  ]},
  { label: 'COLLECTION', items: [
    { path: '/hunt', icon: '🎯', label: 'Narrative Hunt' },
    { path: '/identity', icon: '👤', label: 'Identity Profiler' },
    { path: '/media', icon: '🖼️', label: 'Media Forensics' },
  ]},
  { label: 'INTELLIGENCE', items: [
    { path: '/velocity', icon: '📈', label: 'Velocity Monitor' },
    { path: '/network', icon: '🕸️', label: 'Network Mapper' },
    { path: '/bots', icon: '🤖', label: 'Behaviour Profiler' },
    { path: '/tactics', icon: '🛡️', label: 'DISARM Tactics' },
  ]},
  { label: 'ATTRIBUTION', items: [
    { path: '/infrastructure', icon: '🏗️', label: 'Infrastructure' },
    { path: '/geo', icon: '🌍', label: 'Geo Intelligence' },
  ]},
  { label: 'OUTPUT', items: [
    { path: '/evidence', icon: '🔒', label: 'Evidence Locker', showBadge: true },
    { path: '/reports', icon: '📋', label: 'Report Generator' },
  ]},
];

export default function Sidebar() {
  const { evidenceCount } = useApp();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>
          <span className="brand-icon">🛡️</span>
          SENTINEL
        </h1>
        <div className="brand-sub">Intel Platform v3.0</div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((section) => (
          <div key={section.label}>
            <div className="nav-section-label">{section.label}</div>
            {section.items.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `nav-item ${isActive ? 'active' : ''}`
                }
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
                {item.showBadge && evidenceCount > 0 && (
                  <span className="nav-badge">{evidenceCount}</span>
                )}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="live-indicator">
          <span className="live-dot"></span>
          SENTINEL ONLINE — ALL SYSTEMS
        </div>
      </div>
    </aside>
  );
}
