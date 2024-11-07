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
          const response = await fetch('/api/balance', {
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
          });
          
          // Handle non-JSON responses
          const contentType = response.headers.get('content-type');
          if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Server returned non-JSON response');
          }
  
          const data = await response.json();
          console.log('Plaid response:', data); // Debug log
          
          // Check if there's no access token or if the response indicates no Plaid connection
          if (!response.ok || data.error) {
            if (response.status === 401 || data.error?.error_code === 'ITEM_LOGIN_REQUIRED' || data.error?.error_code === 'NO_ACCESS_TOKEN') {
              isPlaidConnected.value = false;
              loading.value = false;
              return;
            }
            throw new Error(data.error?.error_message || 'Failed to fetch accounts');
          }
  
          isPlaidConnected.value = true;
          accounts.value = data.accounts.map(account => ({
            ...account,
            account_id: account.account_id,
            name: account.name || 'Unknown Account',
            balance: account.balances.available 
              ? `$${account.balances.available.toFixed(2)}` 
              : `$${account.balances.current.toFixed(2)}`,
            status: account.balances.available ? 'Available' : 'Current',
            subtype: account.subtype?.charAt(0).toUpperCase() + account.subtype?.slice(1) || 'Unknown Type'
          }));
  
        } catch (err) {
          console.error('Error fetching accounts:', err); // Debug log
          error.value = err.message;
          isPlaidConnected.value = false;
        } finally {
          loading.value = false;
        }
      };
  
      onMounted(() => {
        if (state.linkSuccess) {
          fetchAccounts();
        } else {
          isPlaidConnected.value = false;
          loading.value = false;
        }
      });
  
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