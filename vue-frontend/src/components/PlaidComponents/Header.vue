<!-- src/components/Header.vue -->
<template>
  <div class="grid">
    <h3 class="title">Plaid Quickstart</h3>

    <div v-if="!state.linkSuccess">
      <h4 class="subtitle">
        A sample end-to-end integration with Plaid
      </h4>
      <p class="introPar">
        The Plaid flow begins when your user wants to connect their bank
        account to your app. Simulate this by clicking the button below to
        launch Link—the client-side component that your users will interact
        with in order to link their accounts to Plaid and allow you to access
        their accounts via the Plaid API.
      </p>
      <!-- Message if backend is not running and there is no link token -->
      <div v-if="!state.backend" class="callout warning">
        <p>
          Unable to fetch link_token: please make sure your backend server
          is running and that your .env file has been configured with your
          <code>PLAID_CLIENT_ID</code> and <code>PLAID_SECRET</code>.
        </p>
      </div>
      <!-- Message if backend is running and there is no link token -->
      <div v-else-if="state.linkToken == null && state.backend" class="callout warning">
        <div>
          Unable to fetch link_token: please make sure your backend server
          is running and that your .env file has been configured correctly.
        </div>
        <div>
          If you are on a Windows machine, please ensure that you have
          cloned the repo with
          <a href="https://github.com/plaid/quickstart#special-instructions-for-windows" target="_blank">
            symlinks turned on
          </a>.
          You can also try checking your
          <a href="https://dashboard.plaid.com/activity/logs" target="_blank">
            activity log
          </a>
          on your Plaid dashboard.
        </div>
        <div>
          Error Code: <code>{{ state.linkTokenError.error_code }}</code>
        </div>
        <div>
          Error Type: <code>{{ state.linkTokenError.error_type }}</code>
        </div>
        <div>
          Error Message: {{ state.linkTokenError.error_message }}
        </div>
      </div>
      <!-- Loading state -->
      <div v-else-if="state.linkToken === ''" class="linkButton">
        <button disabled>Loading...</button>
      </div>
      <!-- Display Link component -->
      <div v-else class="linkButton">
        <!-- Link component needs to be translated into Vue -->
        <Link />
      </div>
    </div>
    <div v-else>
      <div v-if="state.isPaymentInitiation">
        <h4 class="subtitle">
          Congrats! Your payment is now confirmed.
        </h4>
        <div class="callout">
          <p>
            You can see information of all your payments in the
            <a href="https://dashboard.plaid.com/activity/payments" target="_blank">
              Payments Dashboard
            </a>.
          </p>
        </div>
        <p class="requests">
          Now that the 'payment_id' is stored on your server, you can use it
          to access the payment information:
        </p>
      </div>
      <div v-else>
        <div v-if="state.isItemAccess">
          <h4 class="subtitle">
            Congrats! By linking an account, you have created an
            <a href="http://plaid.com/docs/quickstart/glossary/#item" target="_blank">
              Item
            </a>.
          </h4>
        </div>
        <div v-else-if="state.userToken">
          <h4 class="subtitle">
            Congrats! You have successfully linked data to a User.
          </h4>
        </div>
        <div v-else>
          <h4 class="subtitle">
            <div class="callout warning">
              Unable to create an item. Please check your backend server.
            </div>
          </h4>
        </div>
        <div v-if="state.itemId || state.accessToken || state.userToken" class="itemAccessContainer">
          <div v-if="state.itemId" class="itemAccessRow">
            <span class="idName">item_id</span>
            <span class="tokenText">{{ state.itemId }}</span>
          </div>
          <div v-if="state.accessToken" class="itemAccessRow">
            <span class="idName">access_token</span>
            <span class="tokenText">{{ state.accessToken }}</span>
          </div>
          <div v-if="state.userToken" class="itemAccessRow">
            <span class="idName">user_token</span>
            <span class="tokenText">{{ state.userToken }}</span>
          </div>
        </div>
        <div v-if="state.isItemAccess || state.userToken">
          <p class="requests">
            Now that you have
            <span v-if="state.accessToken">an access_token</span
            ><span v-if="state.accessToken && state.userToken"> and </span
            ><span v-if="state.userToken">a user_token</span>, you can make all
            of the following requests:
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { usePlaid } from '../../composables/usePlaid';
// Import Link component, which needs to be translated into Vue
import Link from './Link.vue';

export default defineComponent({
  name: 'Header',
  components: {
    Link,
  },
  setup() {
    const { state } = usePlaid();

    return {
      state,
    };
  },
});
</script>

<style scoped>
/* Simplified styling */
.grid {
  width: 100%;
  display: flex;
  flex-direction: column;
  margin: auto;
  margin-bottom: 20px;
}

.title {
  margin-top: 90px;
  margin-bottom: 0;
  font-weight: 800;
  height: 60px;
}

.subtitle {
  margin-top: 0;
  margin-bottom: 30px;
}

.introPar {
  width: 100%;
  font-size: 18px;
  margin: 20px 0;
}

.linkButton {
  margin-top: 30px;
}

.callout {
  border: 1px solid #ccc;
  padding: 15px;
  margin-bottom: 20px;
}

.callout.warning {
  background-color: #ffe6e6;
  border-color: #ff0000;
}

.itemAccessContainer {
  display: flex;
  flex-direction: column;
  width: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-top: 30px;
  border-radius: 2px;
}

.itemAccessRow {
  display: flex;
  border: 1px solid #e0e0e0;
  margin: 0;
}

.idName {
  padding: 20px 30px 20px 50px;
  flex: 1;
  font-weight: bold;
  font-family: monospace;
  color: #000;
}

.tokenText {
  padding: 20px 30px 20px 0;
  flex: 5;
  font-family: monospace;
}

.requests {
  margin-top: 70px;
  font-size: 18px;
}
</style>
