// vue-frontend/src/utils/formatUtils.js

/**
 * Formats a number as currency
 * @param {number|string} val - Value to format
 * @param {string} currency - Currency code (default: 'USD')
 * @returns {string} Formatted currency string
 */
export function formatCurrency(val, currency = 'USD') {
    if (val === null || val === undefined) return '$0.00';
    
    if (typeof val === 'string') {
      val = parseFloat(val.replace(/[^0-9.-]+/g, '')) || 0;
    }
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(val);
  }
  
  /**
   * Formats a number as a percentage
   * @param {number} val - Value to format (0-100)
   * @param {number} decimals - Number of decimal places
   * @returns {string} Formatted percentage string
   */
  export function formatPercent(val, decimals = 1) {
    if (val === null || val === undefined) return '0%';
    
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(val / 100);
  }
  
  /**
   * Returns a CSS class based on amount value
   * @param {number} val - Amount value
   * @param {string} baseClass - Base CSS class
   * @returns {string} CSS class name
   */
  export function amountClass(val, baseClass = 'text-h5') {
    if (val < 0) return `${baseClass} text-error`;
    if (val > 0) return `${baseClass} text-success`;
    return baseClass;
  }
  
  /**
   * Formats a number with commas
   * @param {number} num - Number to format
   * @returns {string} Formatted number
   */
  export function formatNumber(num, decimals = 0) {
    if (num === null || num === undefined) return '0';
    
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(num);
  }
  
  /**
   * Extracts a numeric value from a string or returns the number
   * @param {string|number} value - Value to parse
   * @returns {number} Numeric value
   */
  export function parseNumericValue(value) {
    if (typeof value === 'number') return value;
    if (!value) return 0;
    
    // Remove all non-numeric characters except decimal point and minus sign
    return parseFloat(value.toString().replace(/[^0-9.-]+/g, '')) || 0;
  }
  
  /**
   * Truncates text with ellipsis if it exceeds maxLength
   * @param {string} text - Text to truncate
   * @param {number} maxLength - Maximum length
   * @returns {string} Truncated text
   */
  export function truncateText(text, maxLength = 20) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    
    return text.substr(0, maxLength - 3) + '...';
  }
  
  /**
   * Formats file size in bytes to human readable format
   * @param {number} bytes - Size in bytes
   * @returns {string} Formatted size
   */
  export function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  /**
   * Converts camelCase to Title Case
   * @param {string} camelCase - CamelCase string
   * @returns {string} Title Case string
   */
  export function camelToTitleCase(camelCase) {
    if (!camelCase) return '';
    
    const result = camelCase.replace(/([A-Z])/g, ' $1');
    return result.charAt(0).toUpperCase() + result.slice(1);
  }
  
  /**
   * Converts snake_case to Title Case
   * @param {string} snakeCase - snake_case string
   * @returns {string} Title Case string
   */
  export function snakeToTitleCase(snakeCase) {
    if (!snakeCase) return '';
    
    return snakeCase
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }
  
  /**
   * Gets a color code based on a value's position in a range
   * @param {number} value - Value to evaluate
   * @param {number} min - Minimum of range
   * @param {number} max - Maximum of range
   * @returns {string} Hex color code
   */
  export function getGradientColor(value, min, max) {
    // Return green for high values, yellow for mid-range, red for low
    const ratio = (value - min) / (max - min);
    
    if (ratio >= 0.67) {
      return '#4caf50'; // Green
    } else if (ratio >= 0.33) {
      return '#ffc107'; // Amber
    } else {
      return '#f44336'; // Red
    }
  }
  
  /**
   * Formats a bank/payment account number with masking
   * @param {string} accountNumber - Account number
   * @returns {string} Masked account number
   */
  export function formatAccountNumber(accountNumber) {
    if (!accountNumber) return '';
    
    // Keep only the last 4 digits visible
    const len = accountNumber.length;
    if (len <= 4) return accountNumber;
    
    return '•••• ' + accountNumber.substring(len - 4);
  }