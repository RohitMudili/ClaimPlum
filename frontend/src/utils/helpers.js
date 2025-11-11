/**
 * Format currency in INR
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency
 */
export const formatCurrency = (amount) => {
  if (amount === null || amount === undefined) return '₹0.00';
  return `₹${Number(amount).toFixed(2)}`;
};

/**
 * Format date to readable string
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Format datetime to readable string
 * @param {string} dateTimeString - ISO datetime string
 * @returns {string} Formatted datetime
 */
export const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return 'N/A';
  const date = new Date(dateTimeString);
  return date.toLocaleString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Get status color class
 * @param {string} status - Status string
 * @returns {string} Tailwind color class
 */
export const getStatusColor = (status) => {
  const statusColors = {
    PENDING: 'bg-yellow-100 text-yellow-800',
    PROCESSING: 'bg-blue-100 text-blue-800',
    COMPLETED: 'bg-green-100 text-green-800',
    FAILED: 'bg-red-100 text-red-800',
  };
  return statusColors[status] || 'bg-gray-100 text-gray-800';
};

/**
 * Get decision color class
 * @param {string} decision - Decision type
 * @returns {string} Tailwind color class
 */
export const getDecisionColor = (decision) => {
  const decisionColors = {
    APPROVED: 'bg-green-100 text-green-800 border-green-300',
    REJECTED: 'bg-red-100 text-red-800 border-red-300',
    PARTIAL: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    MANUAL_REVIEW: 'bg-orange-100 text-orange-800 border-orange-300',
    NOT_A_MEMBER: 'bg-purple-100 text-purple-800 border-purple-300',
  };
  return decisionColors[decision] || 'bg-gray-100 text-gray-800 border-gray-300';
};

/**
 * Get decision icon
 * @param {string} decision - Decision type
 * @returns {string} Unicode emoji/icon
 */
export const getDecisionIcon = (decision) => {
  const icons = {
    APPROVED: '✅',
    REJECTED: '❌',
    PARTIAL: '⚠️',
    MANUAL_REVIEW: '🔍',
    NOT_A_MEMBER: '💼',
  };
  return icons[decision] || '📄';
};

/**
 * Validate file type
 * @param {File} file - File to validate
 * @param {Array} allowedTypes - Allowed MIME types
 * @returns {boolean} Is valid
 */
export const validateFileType = (file, allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg']) => {
  return allowedTypes.includes(file.type);
};

/**
 * Validate file size
 * @param {File} file - File to validate
 * @param {number} maxSize - Max size in bytes (default 10MB)
 * @returns {boolean} Is valid
 */
export const validateFileSize = (file, maxSize = 10 * 1024 * 1024) => {
  return file.size <= maxSize;
};

/**
 * Format file size
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Calculate confidence color
 * @param {number} score - Confidence score (0-1)
 * @returns {string} Tailwind color class
 */
export const getConfidenceColor = (score) => {
  if (score >= 0.8) return 'text-green-600';
  if (score >= 0.6) return 'text-yellow-600';
  return 'text-red-600';
};

/**
 * Truncate text
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export const truncate = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Sleep/delay function
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise} Promise that resolves after delay
 */
export const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
