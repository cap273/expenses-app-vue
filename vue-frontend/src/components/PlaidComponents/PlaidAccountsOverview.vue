<!-- Updated PlaidAccountsOverview.vue -->
<template>
  <v-card class="mt-4" variant="outlined">
    <v-card-title class="d-flex justify-space-between align-center">
      <span>Connected Bank Accounts</span>
      <v-btn
        v-if="isPlaidConnected"
        color="primary"
        variant="text"
        size="small"
        @click="$router.push('/plaid')"
      >
        <v-icon start>mdi-cog</v-icon>
        Manage
      </v-btn>
    </v-card-title>

    <!-- Loading State -->
    <v-card-text v-if="loading" class="d-flex justify-center align-center pa-4">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </v-card-text>

    <!-- Error State -->
    <v-card-text v-else-if="error">
      <v-alert type="error" class="mb-0">
        {{ error }}
      </v-alert>
    </v-card-text>

    <!-- Not Connected State -->
    <v-card-text v-else-if="!isPlaidConnected">
      <v-alert type="info" class="mb-4">
        Connect your bank accounts to automatically track your expenses.
      </v-alert>
      <div class="d-flex justify-center">
        <v-btn color="primary" @click="$router.push('/plaid')">
          <v-icon start>mdi-bank</v-icon>
          Connect Your Bank
        </v-btn>
      </div>
    </v-card-text>

    <!-- Connected Accounts -->
    <v-card-text v-else>
      <v-row>
        <v-col
          v-for="account in accounts"
          :key="account.account_id"
          cols="12"
          sm="6"
          md="4"
        >
          <v-card variant="outlined">
            <v-card-item>
              <v-card-title class="text-subtitle-1">{{ account.name }}</v-card-title>
              <v-card-subtitle v-if="account.official_name">{{ account.official_name }}</v-card-subtitle>
            </v-card-item>

            <v-card-text>
              <div class="text-h6 mb-2">{{ account.balance }}</div>
              <div class="d-flex justify-space-between align-center">
                <div class="text-caption text-medium-emphasis">
                  {{ account.subtype }} Account
                </div>
                <v-chip
                  :color="account.status === 'Available' ? 'success' : 'info'"
                  size="small"
                >
                  {{ account.status }}
                </v-chip>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { ref, onMounted } from 'vue';
import { usePlaid } from '@/composables/usePlaid';

export default {
  name: 'PlaidAccountsOverview',
  setup() {
    const { state } = usePlaid();
    const accounts = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const isPlaidConnected = ref(false);

    const fetchAccounts = async () => {
      try {
        loading.value = true;
        error.value = '';
        
        // First, check if user has any Plaid connections
        const statusResponse = await fetch('/api/plaid_status');
        if (!statusResponse.ok) {
          throw new Error('Failed to fetch Plaid status');
        }
        
        const statusData = await statusResponse.json();
        isPlaidConnected.value = statusData.has_plaid_connections;
        
        if (!isPlaidConnected.value) {
          loading.value = false;
          return;
        }
        
        // Now get account details if connected
        const response = await fetch('/api/get_plaid_items');
        const itemsData = await response.json();
        
        if (!response.ok || !itemsData.success) {
          throw new Error('Failed to fetch Plaid items');
        }
        
        // We'll need to fetch detailed account info for each item
        const balancePromises = [];
        for (const item of itemsData.items) {
          balancePromises.push(
            fetch('/api/balance', {
              headers: {
                'Content-Type': 'application/json'
              }
            })
          );
        }
        
        // Try to get balance info, but don't fail if it doesn't work
        try {
          const balanceResponse = await fetch('/api/balance');
          const balanceData = await balanceResponse.json();
          
          if (balanceResponse.ok && balanceData.accounts) {
            accounts.value = balanceData.accounts.map(account => ({
              account_id: account.account_id,
              name: account.name || 'Unknown Account',
              official_name: account.official_name,
              balance: account.balances.available 
                ? `$${account.balances.available.toFixed(2)}` 
                : `$${account.balances.current.toFixed(2)}`,
              status: account.balances.available ? 'Available' : 'Current',
              subtype: account.subtype?.charAt(0).toUpperCase() + account.subtype?.slice(1) || 'Unknown Type'
            }));
          }
        } catch (err) {
          console.warn('Could not fetch detailed account info:', err);
          // Create placeholder accounts based on items
          accounts.value = itemsData.items.map(item => ({
            account_id: item.item_id,
            name: item.institution_name || 'Connected Account',
            balance: 'Balance unavailable',
            status: 'Connected',
            subtype: 'Bank'
          }));
        }
      } catch (err) {
        console.error('Error fetching accounts:', err);
        error.value = err.message;
        isPlaidConnected.value = false;
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchAccounts);

    return {
      accounts,
      loading,
      error,
      isPlaidConnected
    };
  }
};
</script>

<style scoped>
.v-card-title {
  word-break: break-word;
}

.v-chip {
  font-size: 0.75rem;
}
</style>