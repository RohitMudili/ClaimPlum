export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  UPLOAD_CLAIM: `${API_BASE_URL}/api/claims/upload`,
  PROCESS_CLAIM: `${API_BASE_URL}/api/claims/process`,
  GET_CLAIM: (id) => `${API_BASE_URL}/api/claims/${id}`,
  HEALTH: `${API_BASE_URL}/health`,
};
