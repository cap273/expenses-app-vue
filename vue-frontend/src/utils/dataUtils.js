// vue-frontend/src/utils/dataUtils.js
import { adjustForTimezone } from './dateUtils';
import { parseNumericValue } from './formatUtils';

/**
 * Groups an array of objects by a specified key
 * @param {Array} array - Array to group
 * @param {string|Function} key - Key to group by or function that returns the key
 * @returns {Object} Grouped object
 */
export function groupBy(array, key) {
  return array.reduce((result, item) => {
    const groupKey = typeof key === 'function' ? key(item) : item[key];
    
    // Initialize group if it doesn't exist
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    
    // Add item to group
    result[groupKey].push(item);
    return result;
  }, {});
}

/**
 * Groups expenses by month
 * @param {Array} expenses - Array of expense objects
 * @returns {Object} Expenses grouped by month
 */
export function groupExpensesByMonth(expenses) {
  if (!expenses || !Array.isArray(expenses)) return {};
  
  return groupBy(expenses, (expense) => {
    const date = adjustForTimezone(expense.ExpenseDate);
    const month = date.toLocaleString('default', { month: 'long' });
    const year = date.getFullYear();
    return `${month} ${year}`;
  });
}

/**
 * Converts grouped expenses to a format suitable for month groups UI
 * @param {Object} groupedExpenses - Expenses grouped by month
 * @returns {Array} Array of month group objects
 */
export function convertToMonthGroups(groupedExpenses) {
  return Object.entries(groupedExpenses).map(([month, expenses]) => {
    // Calculate total for the month
    const total = expenses.reduce((sum, expense) => {
      const amount = parseNumericValue(expense.Amount);
      return sum + amount;
    }, 0);
    
    return {
      month,
      expenses,
      total,
      isOpen: true // Default to open
    };
  }).sort((a, b) => {
    // Sort by date, newest first
    const dateA = new Date(a.month);
    const dateB = new Date(b.month);
    return dateB - dateA;
  });
}

/**
 * Gets daily totals for a month
 * @param {Array} expenses - Array of expense objects
 * @param {number} year - Year
 * @param {number} month - Month (0-11)
 * @returns {Array} Array of daily totals
 */
export function getDailyTotals(expenses, year, month) {
  if (!expenses || !Array.isArray(expenses)) return [];
  
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const dailyTotals = Array(daysInMonth).fill(0);
  
  expenses.forEach(expense => {
    const date = adjustForTimezone(expense.ExpenseDate);
    
    if (date.getMonth() === month && date.getFullYear() === year) {
      const dayIndex = date.getDate() - 1; // 0-based index
      const amount = parseNumericValue(expense.Amount);
      dailyTotals[dayIndex] += amount;
    }
  });
  
  return dailyTotals;
}

/**
 * Gets expense totals by category
 * @param {Array} expenses - Array of expense objects
 * @param {number} limit - Maximum number of categories to return
 * @returns {Array} Array of category totals
 */
export function getExpenseTotalsByCategory(expenses, limit = 5) {
  if (!expenses || !Array.isArray(expenses)) return [];
  
  const categoryTotals = {};
  
  expenses.forEach(expense => {
    const category = expense.ExpenseCategory || 'Uncategorized';
    const amount = parseNumericValue(expense.Amount);
    
    if (!categoryTotals[category]) {
      categoryTotals[category] = 0;
    }
    
    categoryTotals[category] += amount;
  });
  
  // Convert to array and sort
  return Object.entries(categoryTotals)
    .map(([category, amount]) => ({ category, amount }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, limit);
}

/**
 * Filters expenses by date range
 * @param {Array} expenses - Array of expense objects
 * @param {Date} startDate - Start date
 * @param {Date} endDate - End date
 * @returns {Array} Filtered expenses
 */
export function filterExpensesByDateRange(expenses, startDate, endDate) {
  if (!expenses || !Array.isArray(expenses)) return [];
  if (!startDate || !endDate) return expenses;
  
  return expenses.filter(expense => {
    const date = adjustForTimezone(expense.ExpenseDate);
    return date >= startDate && date <= endDate;
  });
}

/**
 * Filters expenses by time period
 * @param {Array} expenses - Array of expense objects
 * @param {string} period - Time period ('month', 'year', 'all')
 * @returns {Array} Filtered expenses
 */
export function filterExpensesByPeriod(expenses, period = 'month') {
  if (!expenses || !Array.isArray(expenses)) return [];
  
  const now = new Date();
  
  return expenses.filter(expense => {
    const date = adjustForTimezone(expense.ExpenseDate);
    
    switch(period) {
      case 'month':
        return date.getMonth() === now.getMonth() && 
               date.getFullYear() === now.getFullYear();
      case 'year':
        return date.getFullYear() === now.getFullYear();
      case 'all':
      default:
        return true;
    }
  });
}

/**
 * Gets top N expenses by amount
 * @param {Array} expenses - Array of expense objects
 * @param {number} limit - Maximum number of expenses to return
 * @returns {Array} Top expenses
 */
export function getTopExpenses(expenses, limit = 5) {
  if (!expenses || !Array.isArray(expenses)) return [];
  
  return [...expenses]
    .sort((a, b) => {
      const amountA = parseNumericValue(a.Amount);
      const amountB = parseNumericValue(b.Amount);
      return amountB - amountA;
    })
    .slice(0, limit);
}

/**
 * Gets the most recent expenses
 * @param {Array} expenses - Array of expense objects
 * @param {number} limit - Maximum number of expenses to return
 * @returns {Array} Most recent expenses
 */
export function getRecentExpenses(expenses, limit = 5) {
  if (!expenses || !Array.isArray(expenses)) return [];
  
  return [...expenses]
    .sort((a, b) => {
      const dateA = adjustForTimezone(a.ExpenseDate);
      const dateB = adjustForTimezone(b.ExpenseDate);
      return dateB - dateA;
    })
    .slice(0, limit);
}

/**
 * Calculates the total expenses for a period
 * @param {Array} expenses - Array of expense objects
 * @param {string} period - Time period ('month', 'year', 'all')
 * @returns {number} Total amount
 */
export function calculateTotalExpenses(expenses, period = 'all') {
  const filteredExpenses = filterExpensesByPeriod(expenses, period);
  
  return filteredExpenses.reduce((total, expense) => {
    return total + parseNumericValue(expense.Amount);
  }, 0);
}