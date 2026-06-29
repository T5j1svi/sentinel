import { useState } from 'react';
import { useApp } from '../AppContext';
import api from '../api/sentinel';

export default function Reports() {
  const { huntResults, caseId, caseName } = useApp();
  const [generating, setGenerating] = useState(false);
  const [downloadReady, setDownloadReady] = useState(false);
  const [selectedSections, setSelectedSections] = useState([
    'executive_summary', 'evidence_table', 'network_graph',
    'velocity_chart', 'disarm_breakdown', 'geo_map', 'appendix',
  ]);
  const [reportTitle, setReportTitle] = useState('SENTINEL Intelligence Report');
  const [selectedFormat, setSelectedFormat] = useState('html');

  const sections = [
    { id: 'executive_summary', label: 'Executive Summary', icon: '📝', desc: 'AI-written narrative overview' },
    { id: 'evidence_table', label: 'Evidence Table', icon: '📋', desc: 'All locked evidence with hashes' },
    { id: 'network_graph', label: 'Network Graph', icon: '🕸️', desc: 'Influence network export' },
    { id: 'velocity_chart', label: 'Velocity Chart', icon: '📈', desc: 'Spread timeline' },
    { id: 'disarm_breakdown', label: 'DISARM Breakdown', icon: '🛡️', desc: 'Tactic classification' },
    { id: 'geo_map', label: 'Geographic Map', icon: '🌍', desc: 'Origin & infrastructure map' },
    { id: 'appendix', label: 'Source Appendix', icon: '📎', desc: 'All source URLs with hashes' },
  ];

  const formats = [
    { id: 'html', label: 'HTML', icon: '🌐', desc: 'Web archive' },
    { id: 'pdf', label: 'PDF', icon: '📄', desc: 'Print-ready' },
    { id: 'docx', label: 'DOCX', icon: '📝', desc: 'Editable' },
    { id: 'stix', label: 'STIX 2.1', icon: '🔗', desc: 'Threat intel' },
  ];

  const toggleSection = (id) => {
    setSelectedSections(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    );
  };

  const generateReport = async () => {
    setGenerating(true);
    setDownloadReady(false);
    try {
      await api.generateReport({
        title: reportTitle,
        case_id: caseId,
        include_sections: selectedSections,
        output_format: selectedFormat,
      });
      setDownloadReady(true);
    } catch (err) {
      console.error('Report generation error:', err);
      setDownloadReady(false);
    } finally {
      setGenerating(false);
    }
  };

  const resultCount = huntResults?.total_results || 0;

  return (
    <div className="page-enter">
      <div className="glass-card mb-5">
        <div className="section-header">
          <div>
            <div className="section-title">📋 Report Generator</div>
            <div className="section-subtitle">
              Generate professional intelligence reports from real investigation data.
            </div>
          </div>
        </div>
      </div>

      <div className="grid-2" style={{ gridTemplateColumns: '2fr 1fr' }}>
        <div>
          {/* Title */}
          <div className="glass-card mb-3 no-hover">
            <div className="section-subtitle mb-2">Report Title</div>
            <div className="search-bar">
              <input
                type="text"
                value={reportTitle}
                onChange={(e) => setReportTitle(e.target.value)}
                placeholder="Enter report title..."
              />
            </div>
          </div>

          {/* Sections */}
          <div className="glass-card mb-3 no-hover">
            <div className="section-title mb-3">Report Sections</div>
            <div className="flex flex-col gap-1">
              {sections.map(section => (
                <div
                  key={section.id}
                  className={`chip ${selectedSections.includes(section.id) ? 'active' : ''}`}
                  onClick={() => toggleSection(section.id)}
                  style={{
                    padding: '10px 12px', borderRadius: 'var(--radius-md)',
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    width: '100%',
                  }}
                >
                  <div className="flex items-center gap-3">
                    <span>{section.icon}</span>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '12px' }}>{section.label}</div>
                      <div style={{ fontSize: '10px', opacity: 0.7 }}>{section.desc}</div>
                    </div>
                  </div>
                  <span style={{ fontSize: '14px' }}>
                    {selectedSections.includes(section.id) ? '✅' : '⬜'}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Format */}
          <div className="glass-card mb-3 no-hover">
            <div className="section-title mb-3">Output Format</div>
            <div className="grid-4">
              {formats.map(fmt => (
                <div
                  key={fmt.id}
                  className={`chip ${selectedFormat === fmt.id ? 'active' : ''}`}
                  onClick={() => setSelectedFormat(fmt.id)}
                  style={{
                    padding: '12px', borderRadius: 'var(--radius-md)',
                    textAlign: 'center', flexDirection: 'column', display: 'flex',
                    alignItems: 'center', gap: '4px',
                  }}
                >
                  <span style={{ fontSize: '20px' }}>{fmt.icon}</span>
                  <div style={{ fontWeight: 600, fontSize: '11px' }}>{fmt.label}</div>
                  <div style={{ fontSize: '9px', opacity: 0.7 }}>{fmt.desc}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Generate */}
          <button
            className="btn btn-primary w-full"
            onClick={generateReport}
            disabled={generating || selectedSections.length === 0}
            style={{ padding: '12px', fontSize: '14px' }}
          >
            {generating ? (
              <>
                <span className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></span>
                Generating Report...
              </>
            ) : (
              `📋 Generate ${selectedFormat.toUpperCase()} Report`
            )}
          </button>

          {downloadReady && (
            <div className="alert-card alert-success mt-3">
              <span>✅</span>
              <div style={{ fontSize: '12px', color: 'var(--text-success)' }}>
                Report generated successfully. Check the backend output directory for the file.
              </div>
            </div>
          )}
        </div>

        {/* Preview */}
        <div className="glass-card">
          <div className="section-title mb-3">Report Preview</div>
          <div style={{
            background: 'var(--bg-card)', border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)', padding: '16px', minHeight: '350px',
          }}>
            <div style={{ borderBottom: '2px solid var(--accent-red)', paddingBottom: '10px', marginBottom: '12px' }}>
              <div style={{ fontSize: '14px', fontWeight: 800 }}>🛡️ {reportTitle}</div>
              <div className="text-xs text-muted" style={{ marginTop: '3px' }}>
                Generated by SENTINEL Intel v3.0 | Case: {caseName} | Classification: UNCLASSIFIED
              </div>
            </div>

            {resultCount > 0 && (
              <div className="text-xs text-muted mb-3">
                Based on {resultCount} results from current investigation.
              </div>
            )}

            {selectedSections.includes('executive_summary') && (
              <div className="mb-3">
                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--accent-blue)', marginBottom: '4px' }}>Executive Summary</div>
                <div className="text-xs text-muted" style={{ lineHeight: 1.5 }}>
                  {resultCount > 0
                    ? `Analysis of ${resultCount} results will be summarized with key findings, threat assessment, and recommendations.`
                    : 'Run a hunt to populate this section with real analysis data.'
                  }
                </div>
              </div>
            )}

            {selectedSections.includes('evidence_table') && (
              <div className="mb-3">
                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--accent-blue)', marginBottom: '4px' }}>Evidence Table</div>
                <div className="text-xs text-muted">
                  Locked evidence with SHA-256 hashes, timestamps, and chain of custody.
                </div>
              </div>
            )}

            {selectedSections.length === 0 && (
              <div className="text-xs text-muted" style={{ textAlign: 'center', padding: '30px 0' }}>
                Select report sections to preview
              </div>
            )}

            <div style={{ marginTop: '16px', fontSize: '9px', color: 'var(--text-muted)', borderTop: '1px solid var(--border-subtle)', paddingTop: '8px' }}>
              {selectedSections.length} sections | Format: {selectedFormat.toUpperCase()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
