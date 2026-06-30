import { NavLink } from 'react-router-dom';
import { useApp } from '../AppContext';
import { motion } from 'framer-motion';

const navItems = [
  { label: 'COMMAND', items: [
    { path: '/', icon: '>', label: 'Dashboard' },
  ]},
  { label: 'COLLECTION', items: [
    { path: '/hunt', icon: '>', label: 'Narrative Hunt' },
    { path: '/identity', icon: '>', label: 'Identity Profiler' },
    { path: '/media', icon: '>', label: 'Media Forensics' },
  ]},
  { label: 'INTELLIGENCE', items: [
    { path: '/velocity', icon: '>', label: 'Velocity Monitor' },
    { path: '/network', icon: '>', label: 'Network Mapper' },
    { path: '/bots', icon: '>', label: 'Behaviour Profiler' },
    { path: '/tactics', icon: '>', label: 'DISARM Tactics' },
  ]},
  { label: 'ATTRIBUTION', items: [
    { path: '/infrastructure', icon: '>', label: 'Infrastructure' },
    { path: '/geo', icon: '>', label: 'Geo Intelligence' },
  ]},
  { label: 'OUTPUT', items: [
    { path: '/evidence', icon: '>', label: 'Evidence Locker', showBadge: true },
    { path: '/reports', icon: '>', label: 'Report Generator' },
  ]},
];

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, x: -15 },
  show: { opacity: 1, x: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

export default function Sidebar() {
  const { evidenceCount } = useApp();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1 style={{ textShadow: '0 0 8px var(--accent-green)' }}>
          <span className="brand-icon">#</span> SENTINEL
        </h1>
        <div className="brand-sub">OSINT SECURE TERMINAL</div>
      </div>

      <motion.nav 
        className="sidebar-nav"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        {navItems.map((section) => (
          <div key={section.label}>
            <motion.div variants={itemVariants} className="nav-section-label">{section.label}</motion.div>
            {section.items.map((item) => (
              <motion.div key={item.path} variants={itemVariants} whileHover={{ x: 4 }} whileTap={{ scale: 0.98 }}>
                <NavLink
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
              </motion.div>
            ))}
          </div>
        ))}
      </motion.nav>

      <div className="sidebar-footer">
        <div className="live-indicator">
          <span className="live-dot"></span>
          SENTINEL ONLINE — ALL SYSTEMS
        </div>
      </div>
    </aside>
  );
}
