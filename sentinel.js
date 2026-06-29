/**
 * SENTINEL Intel — API Client
 * Communicates with the FastAPI backend
 */

const API_BASE = 'https://sentinel-mxnq.onrender.com';

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const config = {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error ${response.status}: ${error}`);
    }
    return await response.json();
  } catch (err) {
    console.error(`SENTINEL API Error [${path}]:`, err);
    throw err;
  }
}

export const api = {
  // Health
  health: () => request('/api/health'),
  systemStatus: () => request('/api/system/status'),

  // Dashboard
  getDashboardStats: () => request('/api/dashboard/stats'),

  // Hunt (Module 1)
  getPlatforms: () => request('/api/hunt/platforms'),
  runHunt: (data) =>
    request('/api/hunt', { method: 'POST', body: JSON.stringify(data) }),
  getCaseState: (caseId) => request(`/api/hunt/state/${caseId}`),
  saveCaseState: (caseId, stateUpdate) =>
    request(`/api/hunt/state/${caseId}`, { method: 'POST', body: JSON.stringify(stateUpdate) }),
  uploadFile: (formData) => {
    // Note: don't stringify or set Content-Type for FormData
    return fetch(`${API_BASE}/api/upload`, {
      method: 'POST',
      body: formData,
    }).then(res => {
      if (!res.ok) throw new Error("Upload failed");
      return res.json();
    });
  },

  // Velocity (Module 2)
  getVelocity: (caseId, narrative = '', hours = 168) =>
    request(`/api/velocity/${caseId}?narrative=${encodeURIComponent(narrative)}&hours=${hours}`),

  // Network (Module 3)
  buildNetwork: (results, centerLabel = 'Narrative') =>
    request('/api/network', {
      method: 'POST',
      body: JSON.stringify(results),
      headers: { 'Content-Type': 'application/json' },
    }),

  // Bots (Module 4)
  analyzeBots: (results, caseId = 'live') =>
    request(`/api/bots/analyze?case_id=${caseId}`, {
      method: 'POST',
      body: JSON.stringify(results),
    }),

  // Tactics (Module 5)
  getTaxonomy: () => request('/api/tactics/taxonomy'),
  analyzeTactics: (results, caseId = 'live') =>
    request(`/api/tactics/analyze?case_id=${caseId}`, {
      method: 'POST',
      body: JSON.stringify(results),
    }),

  // Infrastructure (Module 6)
  analyzeInfrastructure: (results, caseId = 'live') =>
    request(`/api/infrastructure/batch?case_id=${caseId}`, {
      method: 'POST',
      body: JSON.stringify(results),
    }),

  // Evidence (Module 7)
  lockEvidence: (data) =>
    request('/api/evidence/lock', { method: 'POST', body: JSON.stringify(data) }),
  getEvidence: (caseId) => request(`/api/evidence/${caseId}`),

  // Geo (Module 8)
  analyzeGeo: (results, caseId = 'live') =>
    request(`/api/geo/analyze?case_id=${caseId}`, {
      method: 'POST',
      body: JSON.stringify(results),
    }),

  // Reports (Module 9)
  generateReport: (data) =>
    request('/api/reports/generate', { method: 'POST', body: JSON.stringify(data) }),
};

export default api;
