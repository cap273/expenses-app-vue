<template>
  <div class="plaid-app-container">
    <div class="plaid-container">
      <h3 class="title">Plaid Quickstart</h3>
      <div v-if="!linkSuccess">
        <h4 class="subtitle">A sample end-to-end integration with Plaid</h4>
        <p class="intro-par">
          The Plaid flow begins when your user wants to connect their bank account to your app. Simulate this by clicking the button below to launch Link - the client-side component that your users will interact with in order to link their accounts to Plaid and allow you to access their accounts via the Plaid API.
        </p>
        <div v-if="linkTokenError">
          <div class="callout warning">
            Unable to fetch link_token: please make sure your backend server is running and that your .env file has been configured correctly.
            <div>
              Error Code: <code>{{ linkTokenError?.error_code }}</code>
            </div>
            <div>
              Error Type: <code>{{ linkTokenError?.error_type }}</code>
            </div>
            <div>Error Message: {{ linkTokenError?.error_message }}</div>
          </div>
        </div>
        <div v-else-if="linkToken === ''">
          <button disabled>Loading...</button>
        </div>
        <div v-else>
          <button @click="launchLink">Link Bank Account</button>
        </div>
      </div>
      <div v-else>
        <div v-if="isPaymentInitiation">
          <h4 class="subtitle">
            Congrats! Your payment is now confirmed.
          </h4>
          <div class="callout">
            You can see information of all your payments in the <a href="https://dashboard.plaid.com/activity/payments" target="_blank">Payments Dashboard</a>.
          </div>
        </div>
        <div v-else>
          <h4 class="subtitle" v-if="isItemAccess">
            Congrats! By linking an account, you have created an
            <a href="http://plaid.com/docs/quickstart/glossary/#item" target="_blank">Item</a>.
          </h4>
          <h4 class="subtitle" v-else-if="userToken">
            Congrats! You have successfully linked data to a User.
          </h4>
          <h4 class="subtitle" v-else>
            <div class="callout warning">
              Unable to create an item. Please check your backend server.
            </div>
          </h4>
          <div class="item-access-container">
            <p v-if="itemId" class="item-access-row">
              <span class="id-name">item_id</span>
              <span class="token-text">{{ itemId }}</span>
            </p>
            <p v-if="accessToken" class="item-access-row">
              <span class="id-name">access_token</span>
              <span class="token-text">{{ accessToken }}</span>
            </p>
            <p v-if="userToken" class="item-access-row">
              <span class="id-name">user_token</span>
              <span class="token-text">{{ userToken }}</span>
            </p>
          </div>
        </div>
        <Products />
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
      backend: true,
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

    const exchangePublicToken = async (public_token) => {
      try {
        const response = await fetch('/api/set_access_token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ public_token }),
        });
        if (!response.ok) {
          throw new Error('Failed to exchange public_token');
        }
        const data = await response.json();
        state.accessToken = data.access_token;
        state.itemId = data.item_id;
        state.linkSuccess = true;
      } catch (error) {
        console.error('Failed to exchange public_token:', error);
      }
    };

    const launchLink = () => {
      if (state.linkToken) {
        loadScript('https://cdn.plaid.com/link/v2/stable/link-initialize.js')
          .then(() => {
            const handler = window.Plaid.create({
              token: state.linkToken,
              onSuccess: async (public_token, metadata) => {
                console.log('Plaid link successful:', public_token, metadata);
                // Exchange the public_token for an access_token and item_id
                await exchangePublicToken(public_token);
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
          .catch((error) => {
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
  margin-bottom: 0.5em
}
.id-name {
  font-weight: bold;
}
.token-text {
  font-family: monospace;
}
</style>