<template>
  <div class="plaid-test-container">
        <!-- Button to open Plaid Link -->
        <plaid-link
          :token="linkToken"
          @onSuccess="handleSuccess"
          @onExit="handleExit"
        >
          Link Bank Account
        </plaid-link>
  </div>
</template>
  
<script>
import { PlaidLink } from '@jcss/vue-plaid-link';

export default {
  components: {
    PlaidLink,
  },

  data() {
    return {
      linkToken: null, // Store the link token here
    };
  },
  async mounted() {
    // Fetch the link token from your backend (Flask API)
    const response = await fetch('/api/create_link_token');
    const { link_token } = await response.json();
    this.linkToken = link_token; // Set the link token
  },
  methods: {
    // Handle successful connection to Plaid
    async handleSuccess(public_token) {
      // Send the public_token to your backend to exchange for an access_token
      const response = await fetch('/api/exchange_public_token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ public_token }),
      });
      const data = await response.json();
      console.log(data); // Handle success response (e.g., display accounts or transactions)
    },
    // Handle when the user exits the Plaid Link flow
    handleExit(err) {
      if (err != null) {
        console.error('User exited Plaid Link flow with an error:', err);
      } else {
        console.log('User exited Plaid Link without error.');
      }
    },
  },
};
</script>
  
<style scoped>
.plaid-test-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh; /* Full height of the viewport */
}
</style>
