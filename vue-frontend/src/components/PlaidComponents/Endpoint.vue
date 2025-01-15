<!-- src/components/Endpoint.vue -->
<template>
  <div class="endpoint">
    <h2>{{ displayName }}</h2>
    <p>{{ description }}</p>
    <div v-if="loading">Loading data...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <Table :data="data" :categories="categories" :isIdentity="isIdentity" />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { usePlaid } from '../../composables/usePlaid';
import Table from './Table.vue';
// Import necessary categories and transformation functions
import {
  transactionsCategories,
  balanceCategories,
  accountsCategories,
  itemCategories,
  transformTransactionsData,
  transformBalanceData,
  transformAccountsData,
  transformItemData,
} from '../../utils/dataUtilities';

export default {
  name: 'Endpoint',
  components: {
    Table,
  },
  props: {
    endpoint: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const { state } = usePlaid();
    const data = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const displayName = ref('');
    const description = ref('');
    const categories = ref([]);
    const transformData = ref(null);
    const schema = ref('');
    const isIdentity = ref(false);

    // Map of endpoint configurations
    const endpointConfig = {
      transactions: {
        name: 'Transactions',
        description:
          'Retrieve transactions or incremental updates for credit and depository accounts.',
        categories: transactionsCategories,
        transformData: transformTransactionsData,
        schema: '/transactions', // Changed from '/transactions/sync' to '/transactions'
        method: 'GET',
      },
      balance: {
        name: 'Balance',
        description:
          'Check balances in real time to prevent non-sufficient funds fees.',
        categories: balanceCategories,
        transformData: transformBalanceData,
        schema: '/balance', // Update if necessary
        method: 'GET',
      },
      accounts: {
        name: 'Accounts',
        description:
          'Retrieve high-level information about all accounts associated with an item.',
        categories: accountsCategories,
        transformData: transformAccountsData,
        schema: '/accounts', // Changed from '/accounts/get' to '/accounts'
        method: 'GET',
      },
      item: {
        name: 'Item',
        description:
          'Retrieve information about an Item, like the institution, billed products, available products, and webhook information.',
        categories: itemCategories,
        transformData: transformItemData,
        schema: '/item', // Changed from '/item/get' to '/item'
        method: 'GET',
      },
    };

    let config = null;

    const fetchData = async () => {
      loading.value = true;
      error.value = null;

      try {
        // Ensure that the access token is available
        if (!state.accessToken && !state.userToken) {
          throw new Error('Access token or user token is not available.');
        }

        const requestBody = {
          access_token: state.accessToken,
          user_token: state.userToken,
        };

        let url = `/api${config.schema}`;
        const options = {
          method: config.method,
          headers: {},
        };

        if (config.method === 'GET') {
          // For GET requests, include parameters in the URL
          const params = new URLSearchParams();
          if (state.accessToken) params.append('access_token', state.accessToken);
          if (state.userToken) params.append('user_token', state.userToken);
          url += `?${params.toString()}`;
        } else {
          // For POST requests, include body
          options.headers['Content-Type'] = 'application/json';
          options.body = JSON.stringify(requestBody);
        }

        const response = await fetch(url, options);

        if (!response.ok) {
          throw new Error(`API request failed with status ${response.status}`);
        }

        const jsonData = await response.json();

        // Log jsonData and all_transactions to the console
        console.log('Full API Response:', jsonData);
        if (jsonData.all_transactions) {
          console.log('All Transactions:', jsonData.all_transactions);
        } else {
          console.log('No all_transactions property found in the API response.');
        }

        // Handle API errors
        if (jsonData.error) {
          throw new Error(jsonData.error.message || 'API returned an error');
        }

        data.value = transformData.value(jsonData);
      } catch (err) {
        error.value = err.message;
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      config = endpointConfig[props.endpoint];
      if (!config) {
        error.value = `No configuration found for endpoint '${props.endpoint}'`;
        loading.value = false;
        return;
      }

      displayName.value = config.name;
      description.value = config.description;
      categories.value = config.categories;
      transformData.value = config.transformData;
      schema.value = config.schema;
      isIdentity.value = props.endpoint === 'identity';

      fetchData();
    });

    return {
      data,
      loading,
      error,
      categories,
      description,
      displayName,
      isIdentity,
    };
  },
};
</script>

<style scoped>
/* Same styles as before */
</style>
