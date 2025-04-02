// src/utils/dataUtilities.js

// Utility function to format currency
const formatCurrency = (number, code) => {
    if (number != null && number !== undefined) {
      return ` ${parseFloat(number.toFixed(2)).toLocaleString("en")} ${code}`;
    }
    return "no data";
  };
  
  // Category definitions for various products
  
  export const transactionsCategories = [
    { title: "Name", field: "name" },
    { title: "Amount", field: "amount" },
    { title: "Date", field: "date" },
  ];
  
  export const balanceCategories = [
    { title: "Name", field: "name" },
    { title: "Balance", field: "balance" },
    { title: "Subtype", field: "subtype" },
    { title: "Mask", field: "mask" },
  ];
  
  export const accountsCategories = [
    { title: "Name", field: "name" },
    { title: "Balance", field: "balance" },
    { title: "Subtype", field: "subtype" },
    { title: "Mask", field: "mask" },
  ];
  
  export const itemCategories = [
    { title: "Institution Name", field: "name" },
    { title: "Billed Products", field: "billed" },
    { title: "Available Products", field: "available" },
  ];
  
  // Data transformation functions
  
  export const transformTransactionsData = (data) => {
    return data.latest_transactions.map((t) => {
      return {
        name: t.name,
        amount: formatCurrency(t.amount, t.iso_currency_code),
        date: t.date,
      };
    });
  };
  
  export const transformBalanceData = (data) => {
    return data.accounts.map((account) => {
      const balance = account.balances.available || account.balances.current;
      return {
        name: account.name,
        balance: formatCurrency(balance, account.balances.iso_currency_code),
        subtype: account.subtype,
        mask: account.mask,
      };
    });
  };
  
  export const transformAccountsData = (data) => {
    return data.accounts.map((account) => {
      const balance = account.balances.available || account.balances.current;
      return {
        name: account.name,
        balance: formatCurrency(balance, account.balances.iso_currency_code),
        subtype: account.subtype,
        mask: account.mask,
      };
    });
  };
  
  export const transformItemData = (data) => {
    return [
      {
        name: data.institution.name,
        billed: data.item.billed_products.join(", "),
        available: data.item.available_products.join(", "),
      },
    ];
  };

  //Plaid Bank Helpers
  export const getBankName = (accountId) => {
    if (!accountId || !plaidAccounts.value[accountId]) {
      return 'Unknown Account';
    }
    const account = plaidAccounts.value[accountId];
    return account.institution || 'Unknown Bank';
  };

  export const getBankAccountDetails = (accountId) => {
    if (!accountId || !plaidAccounts.value[accountId]) {
      return 'Unknown Account';
    }
    const account = plaidAccounts.value[accountId];
    const type = account.type
      ? account.type.charAt(0).toUpperCase() + account.type.slice(1)
      : '';
    const subtype = account.subtype
      ? account.subtype.charAt(0).toUpperCase() + account.subtype.slice(1)
      : '';
    const mask = account.mask ? `****${account.mask}` : '';
    return `${account.name || 'Account'} (${type} ${subtype}) ${mask}`;
  };

/**
 * Gets a formatted category name from Plaid transaction data
 * @param {Object} expense - Expense object with potential Plaid categorization
 * @returns {string} - Formatted category name
 */
export const getPlaidCategory = (expense) => {
  // First, try to use ExpenseCategory if it exists and is not null
  if (expense.ExpenseCategory) {
    return expense.ExpenseCategory;
  }
  
  // If no ExpenseCategory, try to use Plaid's personal finance categories
  if (expense.PlaidPersonalFinanceCategoryPrimary) {
    // Transform the category from UPPERCASE_WITH_UNDERSCORES to Title Case With Spaces
    const formattedCategory = expense.PlaidPersonalFinanceCategoryPrimary
      .replace(/_/g, ' ')
      .toLowerCase()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
      
    return formattedCategory;
  }
  
  // Use merchant name or transaction name as a fallback
  return expense.PlaidMerchantName || expense.PlaidName || 'Uncategorized';
};
  
  // Export all utilities
  export default {
    formatCurrency,
    transactionsCategories,
    balanceCategories,
    accountsCategories,
    itemCategories,
    transformTransactionsData,
    transformBalanceData,
    transformAccountsData,
    transformItemData,
  };
  