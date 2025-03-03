// src/utils/dateUtils.js
/*
export function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const date = new Date(dateString);
    const formattedDate = new Intl.DateTimeFormat('en-US', options).format(
      new Date(
        date.getUTCFullYear(),
        date.getUTCMonth(),
        date.getUTCDate()
      )
    );
    return formattedDate;
  }
    */
  
  export function parseDateInUTC(dateString) {
    const date = new Date(dateString);
    return new Date(
      Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate())
    );
  }

  // vue-frontend/src/utils/dateUtils.js

/**
 * Adjusts a date string for timezone issues (prevents date shifts)
 * @param {string} dateString - Date string to adjust
 * @returns {Date} Adjusted Date object
 */
export function adjustForTimezone(dateString) {
  if (!dateString) return new Date();
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return new Date();
  const timezoneOffset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() + timezoneOffset);
}

/**
 * Formats a date to a localized string
 * @param {string|Date} dateStr - Date string or object to format
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export function formatDate(dateStr, options = { year: 'numeric', month: 'long', day: 'numeric' }) {
  if (!dateStr) return '';
  const d = typeof dateStr === 'string' ? adjustForTimezone(dateStr) : dateStr;
  return d.toLocaleDateString(undefined, options);
}

/**
 * Returns short format date (e.g., "Jan 15, 2023")
 * @param {string|Date} dateStr - Date to format
 * @returns {string} Formatted date
 */
export function formatShortDate(dateStr) {
  return formatDate(dateStr, { year: 'numeric', month: 'short', day: 'numeric' });
}

/**
 * Gets number of days in a month
 * @param {number} year - Year
 * @param {number} month - Month (0-11)
 * @returns {number} Number of days
 */
export function daysInMonth(year, month) {
  return new Date(year, month + 1, 0).getDate();
}

/**
 * Gets month name from month number
 * @param {number} monthIndex - Month index (0-11)
 * @returns {string} Month name
 */
export function getMonthName(monthIndex) {
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  return months[monthIndex];
}

/**
 * Gets month name from date with optional offset
 * @param {number} monthOffset - Month offset from current month
 * @returns {string} Month name
 */
export function getRelativeMonthName(monthOffset = 0) {
  const date = new Date();
  date.setMonth(date.getMonth() - monthOffset);
  return getMonthName(date.getMonth());
}

/**
 * Returns array of day indices for a month
 * @param {number} year - Year
 * @param {number} month - Month (0-11)
 * @returns {Array} Array of day indices (1-31)
 */
export function getDaysArray(year, month) {
  const numDays = daysInMonth(year, month);
  return Array.from({ length: numDays }, (_, i) => i + 1);
}

/**
 * Get start and end date for a specific month
 * @param {number} year - Year
 * @param {number} month - Month (0-11)
 * @returns {object} Object with start and end dates
 */
export function getMonthDateRange(year, month) {
  const startDate = new Date(year, month, 1);
  const endDate = new Date(year, month + 1, 0);
  return { startDate, endDate };
}

/**
 * Check if a date is within the current month
 * @param {Date|string} date - Date to check
 * @returns {boolean} True if date is in current month
 */
export function isCurrentMonth(date) {
  const checkDate = typeof date === 'string' ? adjustForTimezone(date) : date;
  const now = new Date();
  return checkDate.getMonth() === now.getMonth() && 
         checkDate.getFullYear() === now.getFullYear();
}

/**
 * Check if a date is within the current year
 * @param {Date|string} date - Date to check
 * @returns {boolean} True if date is in current year
 */
export function isCurrentYear(date) {
  const checkDate = typeof date === 'string' ? adjustForTimezone(date) : date;
  return checkDate.getFullYear() === new Date().getFullYear();
}

/**
 * Get formatted date range string (e.g., "Jan 1 - Jan 31, 2023")
 * @param {Date} startDate - Start date
 * @param {Date} endDate - End date 
 * @returns {string} Formatted date range
 */
export function formatDateRange(startDate, endDate) {
  const sameYear = startDate.getFullYear() === endDate.getFullYear();
  const sameMonth = startDate.getMonth() === endDate.getMonth();
  
  if (sameYear && sameMonth) {
    return `${startDate.toLocaleDateString(undefined, { month: 'short' })} ${startDate.getDate()} - ${endDate.getDate()}, ${startDate.getFullYear()}`;
  } else if (sameYear) {
    return `${startDate.toLocaleDateString(undefined, { month: 'short' })} ${startDate.getDate()} - ${endDate.toLocaleDateString(undefined, { month: 'short' })} ${endDate.getDate()}, ${startDate.getFullYear()}`;
  } else {
    return `${startDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })} - ${endDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
  }
}