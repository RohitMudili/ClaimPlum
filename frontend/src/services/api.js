import axios from 'axios';
import { API_BASE_URL } from '../config';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for document processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Upload claim documents
 * @param {Object} data - Form data with member_id, prescription, bill, etc.
 * @returns {Promise} Upload response
 */
export const uploadClaim = async (data) => {
  const formData = new FormData();

  // Only append fields that have values
  if (data.member_id) formData.append('member_id', data.member_id);
  if (data.prescription) formData.append('prescription', data.prescription);
  if (data.bill) formData.append('bill', data.bill);

  // Optional fields for non-members
  if (data.member_name) formData.append('member_name', data.member_name);
  if (data.contact_email) formData.append('contact_email', data.contact_email);
  if (data.contact_phone) formData.append('contact_phone', data.contact_phone);

  const response = await api.post('/api/claims/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Process uploaded claim
 * @param {string} claimId - Claim ID to process
 * @returns {Promise} Processing result with decision
 */
export const processClaim = async (claimId) => {
  const response = await api.post(`/api/claims/process/${claimId}`);
  return response.data;
};

/**
 * Get claim details
 * @param {string} claimId - Claim ID
 * @returns {Promise} Claim details
 */
export const getClaim = async (claimId) => {
  const response = await api.get(`/api/claims/${claimId}`);
  return response.data;
};

/**
 * List all claims with optional filters
 * @param {Object} filters - { member_id, status }
 * @returns {Promise} List of claims
 */
export const listClaims = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.member_id) params.append('member_id', filters.member_id);
  if (filters.status) params.append('status', filters.status);

  const response = await api.get(`/api/claims?${params.toString()}`);
  return response.data;
};

/**
 * Create new member
 * @param {Object} memberData - Member information
 * @returns {Promise} Created member
 */
export const createMember = async (memberData) => {
  const response = await api.post('/api/members', memberData);
  return response.data;
};

/**
 * Get member details
 * @param {string} memberId - Member ID
 * @returns {Promise} Member details
 */
export const getMember = async (memberId) => {
  const response = await api.get(`/api/members/${memberId}`);
  return response.data;
};

/**
 * Get member's claim history
 * @param {string} memberId - Member ID
 * @returns {Promise} Member's claims
 */
export const getMemberClaims = async (memberId) => {
  const response = await api.get(`/api/members/${memberId}/claims`);
  return response.data;
};

/**
 * Health check
 * @returns {Promise} Health status
 */
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
