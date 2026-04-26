const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const fetchLatest = () => fetch(`${BASE}/api/latest`).then(r => r.json());
export const fetchHistory = (limit = 90) => fetch(`${BASE}/api/history?limit=${limit}`).then(r => r.json());
export const fetchRuns = (limit = 50, offset = 0) => fetch(`${BASE}/api/runs?limit=${limit}&offset=${offset}`).then(r => r.json());
