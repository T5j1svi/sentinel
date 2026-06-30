import { useState } from 'react';
import MetricCard from '../components/MetricCard';

export default function Media() {
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [mockResult, setMockResult] = useState(null);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    runMockAnalysis();
  };
  
  const runMockAnalysis = () => {
    setLoading(true);
    setMockResult(null);
    setTimeout(() => {
      setLoading(false);
      setMockResult({
        deepfakeProb: "89.4%",
        exif: "Removed / Stripped",
        camera: "Unknown (AI Gen Artifacts)",
        matches: 4
      });
    }, 2500);
  };

  return (
    <div className="page-enter">
      <div className="glass-card mb-5">
        <div className="section-header">
          <div>
            <div className="section-title">🖼️ Media Forensics</div>
            <div className="section-subtitle">
              Image & video analysis — EXIF extraction, reverse image search, deepfake detection.
            </div>
          </div>
          <span className="badge badge-info">COMING SOON</span>
        </div>
      </div>

      {/* Upload area */}
      {!loading && !mockResult && (
        <div
          className="glass-card mb-5"
          style={{
            borderStyle: 'dashed',
            borderWidth: '2px',
            borderColor: dragOver ? 'var(--accent-blue)' : 'var(--border-default)',
            background: dragOver ? 'var(--accent-blue-glow)' : 'var(--bg-glass)',
            transition: 'all 0.2s ease',
            cursor: 'pointer',
          }}
          onClick={runMockAnalysis}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
        >
          <div className="empty-state" style={{ padding: '40px 20px' }}>
            <div className="empty-icon">📤</div>
            <div className="empty-title">Drop Media Here</div>
            <div className="empty-text">
              Drag and drop an image/video or click here to run a mock analysis.
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="glass-card mb-5">
          <div className="flex items-center gap-3">
            <span className="spinner" style={{ borderColor: 'var(--accent-red)', borderTopColor: 'transparent' }}></span>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>[ SYSTEM ] Scanning File Pixels...</div>
              <div className="text-xs" style={{ color: 'var(--accent-blue)' }}>Running AI Detection & pHash comparison...</div>
            </div>
          </div>
          <div className="progress-bar mt-3" style={{ background: 'rgba(0,0,0,0.5)' }}>
            <div className="progress-fill" style={{ width: '65%', background: 'var(--accent-red)', boxShadow: 'var(--shadow-glow-red)' }}></div>
          </div>
        </div>
      )}

      {mockResult && (
        <div className="animate-fade-in">
          <div className="metrics-grid">
            <MetricCard icon="🤖" value={mockResult.deepfakeProb} label="AI Gen Probability" accentColor="var(--accent-red)" />
            <MetricCard icon="📸" value={mockResult.camera} label="Source Camera" accentColor="var(--accent-purple)" />
            <MetricCard icon="🔍" value={mockResult.matches} label="Reverse Matches" accentColor="var(--accent-amber)" />
          </div>
          
          <div className="glass-card mb-5" style={{ borderLeft: '4px solid var(--accent-red)' }}>
            <div className="section-title text-danger mb-2">CRITICAL ALERT: Media Manipulation Detected</div>
            <p className="text-sm text-muted">SENTINEL algorithms have detected high probability of Generative AI artifacts around the facial structure and lighting reflections. The EXIF metadata was intentionally stripped to hide origin.</p>
            <button className="btn btn-ghost btn-sm mt-3" onClick={() => setMockResult(null)}>{'< '} Reset Scan</button>
          </div>
        </div>
      )}

      {/* Feature preview */}
      <div className="grid-3">
        <div className="glass-card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '28px', marginBottom: '8px' }}>🔍</div>
          <div style={{ fontSize: '13px', fontWeight: 700, marginBottom: '4px' }}>EXIF Extraction</div>
          <div className="text-xs text-muted">
            Camera model, GPS coordinates, timestamp, software used. Identifies metadata inconsistencies.
          </div>
        </div>
        <div className="glass-card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '28px', marginBottom: '8px' }}>🔄</div>
          <div style={{ fontSize: '13px', fontWeight: 700, marginBottom: '4px' }}>Reverse Search</div>
          <div className="text-xs text-muted">
            Search across Google, Yandex, and TinEye to find original source and detect reuse.
          </div>
        </div>
        <div className="glass-card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '28px', marginBottom: '8px' }}>🤖</div>
          <div style={{ fontSize: '13px', fontWeight: 700, marginBottom: '4px' }}>Deepfake Detection</div>
          <div className="text-xs text-muted">
            AI-powered analysis to detect manipulated or AI-generated images and videos.
          </div>
        </div>
      </div>
    </div>
  );
}
