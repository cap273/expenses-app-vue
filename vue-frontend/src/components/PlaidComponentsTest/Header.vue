<template>
    <div class="plaid-app-container">
      <div class="plaid-container">
        <Header :linkSuccess="linkSuccess" :isPaymentInitiation="isPaymentInitiation" :itemId="itemId" :accessToken="accessToken" :userToken="userToken" :backend="backend" :linkTokenError="linkTokenError" />
        <div v-if="linkSuccess">
          <Products v-if="products.length" />
          <Items v-if="!isPaymentInitiation && itemId" />
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { defineComponent, onMounted, reactive, computed } from 'vue';
  import Products from '@/components/PlaidComponentsTest/Products.vue';
  import Items from '@/components/PlaidComponentsTest/Items.vue';
  import { CraCheckReportProduct } from 'plaid';
  import { loadScript } from 'vue-plugin-load-script';
  
  export default defineComponent({
    components: {
      Products,
      Items,
      Header,
    },
    setup() {
      const state = reactive({
        linkSuccess: false,
        isPaymentInitiation: false,
        itemId: null,
        accessToken: null,
        userToken: null,
        products: [],
        linkToken: null,
        linkTokenError: null,
        isUserTokenFlow: false,
        isCraProductsExclusively: false,
        backend: true, // Assume backend is running initially
      });
  
      const isItemAccess = computed(() => state.itemId != null);
  
      const getInfo = async () => {
        try {
          const response = await fetch('/api/info', { method: 'POST' });
          if (!response.ok) {
            throw new Error('Failed to fetch backend info');
          }
          const data = await response.json();
          const paymentInitiation = data.products.includes('payment_initiation');
          const craEnumValues = Object.values(CraCheckReportProduct);
          const isUserTokenFlow = data.products.some(product => craEnumValues.includes(product));
          const isCraProductsExclusively = data.products.every(product => craEnumValues.includes(product));
  
          state.products = data.products;
          state.isPaymentInitiation = paymentInitiation;
          state.isUserTokenFlow = isUserTokenFlow;
          state.isCraProductsExclusively = isCraProductsExclusively;
  
          return { paymentInitiation, isUserTokenFlow };
        } catch (error) {
          console.error('Failed to get info:', error);
          state.backend = false;
        }
      };
  
      const generateUserToken = async () => {
        try {
          const response = await fetch('/api/create_user_token', { method: 'POST' });
          if (!response.ok) {
            throw new Error('Failed to create user token');
          }
          const data = await response.json();
          if (data && data.error == null) {
            state.userToken = data.user_token;
          } else {
            state.linkToken = null;
            state.linkTokenError = data.error;
          }
        } catch (error) {
          console.error('Failed to generate user token:', error);
          state.linkTokenError = { error_message: error.message };
        }
      };
  
      const generateToken = async (isPaymentInitiation) => {
        const path = isPaymentInitiation ? '/api/create_link_token_for_payment' : '/api/create_link_token';
        try {
          const response = await fetch(path, { method: 'POST' });
          if (!response.ok) {
            throw new Error('Failed to create link token');
          }
          const data = await response.json();
          if (data && data.link_token) {
            state.linkToken = data.link_token;
            localStorage.setItem('link_token', data.link_token);
          } else {
            state.linkToken = null;
            state.linkTokenError = data.error;
          }
        } catch (error) {
          console.error('Failed to generate link token:', error);
          state.linkTokenError = { error_message: error.message };
        }
      };
  
      const launchLink = () => {
        if (state.linkToken) {
          loadScript('https://cdn.plaid.com/link/v2/stable/link-initialize.js')
            .then(() => {
              const handler = window.Plaid.create({
                token: state.linkToken,
                onSuccess: (public_token, metadata) => {
                  console.log('Plaid link successful:', public_token, metadata);
                  // Send public_token to server to exchange for access_token
                  state.linkSuccess = true;
                },
                onExit: (err, metadata) => {
                  if (err != null) {
                    console.error('User exited Plaid Link flow with an error:', err);
                  } else {
                    console.log('User exited Plaid Link without error.', metadata);
                  }
                },
                onEvent: (eventName, metadata) => {
                  console.log('Event:', eventName, metadata);
                },
              });
              handler.open();
            })
            .catch(error => {
              console.error('Failed to load Plaid Link script:', error);
            });
        }
      };
  
      onMounted(async () => {
        const { paymentInitiation, isUserTokenFlow } = await getInfo();
  
        if (window.location.href.includes('?oauth_state_id=')) {
          state.linkToken = localStorage.getItem('link_token');
          return;
        }
  
        if (isUserTokenFlow) {
          await generateUserToken();
        }
        await generateToken(paymentInitiation);
      });
  
      return {
        ...state,
        isItemAccess,
        launchLink,
      };
    },
  });
  </script>
  
  <style scoped>
  .plaid-app-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
  }
  .plaid-container {
    width: 80%;
    max-width: 800px;
  }
  .title {
    font-size: 1.5em;
    margin-bottom: 0.5em;
  }
  .subtitle {
    font-size: 1.2em;
    margin-bottom: 1em;
  }
  .intro-par {
    margin-bottom: 1.5em;
  }
  .callout {
    margin-bottom: 1em;
    padding: 1em;
    background-color: #ffefef;
    border: 1px solid #ffcccc;
  }
  .warning {
    color: #cc0000;
  }
  .linkButton {
    margin-bottom: 1.5em;
  }
  .item-access-container {
    margin-top: 1.5em;
  }
  .item-access-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5em;
  }
  .id-name {
    font-weight: bold;
  }
  .token-text {
    font-family: monospace;
  }
  </style>
  