import { useState } from 'react';

export default function Media() {
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    // Future: handle file upload to backend
    const files = Array.from(e.dataTransfer.files);
    console.log('Dropped files:', files);
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
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <div className="empty-state" style={{ padding: '40px 20px' }}>
          <div className="empty-icon">📤</div>
          <div className="empty-title">Drop Media Here</div>
          <div className="empty-text">
            Drag and drop an image or video file to analyze. Supported: JPG, PNG, WebP, MP4, MOV.
          </div>
        </div>
      </div>

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
