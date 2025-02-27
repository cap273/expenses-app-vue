// src/composables/usePlaid.js
import { reactive, readonly, onMounted } from 'vue';
import { CraCheckReportProduct } from 'plaid';

// Define the initial state at the module level
const initialState = {
  linkSuccess: false,
  isItemAccess: true,
  isPaymentInitiation: false,
  isCraProductsExclusively: false,
  isUserTokenFlow: false,
  linkToken: "", // Ensures no error message on load
  userToken: null,
  accessToken: null,
  itemId: null,
  isError: false,
  backend: true,
  products: ["transactions"],
  linkTokenError: {
    error_type: "",
    error_code: "",
    error_message: "",
  },
};

// Create a reactive state at the module level
const state = reactive({ ...initialState });

// Define your functions at the module level
function updateState(newState) {
  Object.assign(state, newState); // Merge the new state values
}

// Function to fetch information about products
async function getInfo() {
  try {
    const response = await fetch('/api/info', { method: 'POST' });
    if (!response.ok) throw new Error('Failed to fetch info');

    const data = await response.json();
    // Set state values based on the response
    updateState({
      isPaymentInitiation: data.products.includes('payment_initiation'),
      isUserTokenFlow: data.products.some((product) =>
        Object.values(CraCheckReportProduct).includes(product)
      ),
      isCraProductsExclusively: data.products.every((product) =>
        Object.values(CraCheckReportProduct).includes(product)
      ),
      products: data.products,
    });
  } catch (error) {
    updateState({ backend: false });
  }
}

// Function to generate a user token
async function generateUserToken() {
  try {
    const response = await fetch('/api/create_user_token', { method: 'POST' });
    if (!response.ok) throw new Error('Failed to generate user token');

    const data = await response.json();
    if (data.error) {
      updateState({ linkTokenError: data.error });
    } else {
      updateState({ userToken: data.user_token });
    }
  } catch (error) {
    updateState({ userToken: null });
  }
}

// Function to generate a link token
async function generateToken(isPaymentInitiationFlow) {
  const path = isPaymentInitiationFlow
    ? '/api/create_link_token_for_payment'
    : '/api/create_link_token';

  try {
    const response = await fetch(path, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to generate link token');

    const data = await response.json();
    if (data.error) {
      updateState({ linkTokenError: data.error });
    } else {
      updateState({ linkToken: data.link_token });
      localStorage.setItem('link_token', data.link_token);
    }
  } catch (error) {
    updateState({ linkToken: null });
  }
}

// Initialize the state
async function init() {
  await getInfo();
  if (window.location.href.includes('?oauth_state_id=')) {
    updateState({ linkToken: localStorage.getItem('link_token') });
  } else {
    if (state.isUserTokenFlow) {
      await generateUserToken();
    }
    await generateToken(state.isPaymentInitiation);
  }
}

// Export the usePlaid function
export function usePlaid() {
  // Set up the init function to run when the composable is used
  onMounted(init);

  return {
    state: readonly(state), // Expose a read-only version of the state
    updateState,
    getInfo,
    generateUserToken,
    generateToken,
    init, // Expose init if you want to call it manually
  };
}

// Optionally, export the functions directly for use outside of usePlaid()
export {
  state, // Be cautious with exporting reactive state directly
  updateState,
  getInfo,
  generateUserToken,
  generateToken,
  init,
};

// This modifies parts of src/composables/usePlaid.js
// Update the submitPlaidTransactions function to use our new API

/**
 * Submits Plaid transactions to the backend.
 *
 * @param {Array} plaidTransactions - Array of Plaid transaction objects.
 * @param {number|string} scope - The scope ID to associate with these transactions.
 * @returns {Promise<Object>} The server's JSON response.
 */
export async function submitPlaidTransactions(plaidTransactions, scope) {
  try {
    const response = await fetch('/api/submit_plaid_transactions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        scope_id: scope, // Renamed for consistency with backend
        plaid_transactions: plaidTransactions,
      }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const responseData = await response.json();
    console.log('Server response:', responseData);
    return responseData;
  } catch (error) {
    console.error('Error submitting Plaid transactions:', error);
    throw error;
  }
}
