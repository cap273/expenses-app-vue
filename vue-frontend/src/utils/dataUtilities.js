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
  