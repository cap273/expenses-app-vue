<!-- PlaidAccountsOverview.vue -->
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
          v-for="item in plaidItems"
          :key="item.item_id"
          cols="12"
          sm="6"
          md="4"
        >
          <v-card variant="outlined">
            <v-card-item>
              <v-card-title class="text-subtitle-1">{{ item.institution_name }}</v-card-title>
              <v-card-subtitle v-if="item.last_synced">
                Last synced: {{ formatDate(item.last_synced) }}
              </v-card-subtitle>
            </v-card-item>

            <v-card-text>
              <div v-if="itemAccountsLoaded[item.item_id]">
                <div v-if="itemAccounts[item.item_id] && itemAccounts[item.item_id].length > 0">
                  <div v-for="account in itemAccounts[item.item_id]" :key="account.account_id" class="mb-3">
                    <div class="d-flex justify-space-between align-center">
                      <div class="text-subtitle-2">{{ account.name }}</div>
                      <div class="text-h6">{{ formatCurrency(account.balances.available || account.balances.current) }}</div>
                    </div>
                    <div class="text-caption text-medium-emphasis">
                      {{ formatAccountType(account.type, account.subtype) }}
                    </div>
                  </div>
                </div>
                <div v-else class="text-center text-medium-emphasis">
                  <p>No accounts found</p>
                </div>
              </div>
              <div v-else class="text-center py-2">
                <v-progress-circular indeterminate size="24" width="2" color="primary"></v-progress-circular>
                <p class="mt-2">Loading accounts...</p>
              </div>
            </v-card-text>

            <v-card-actions>
              <v-btn
                variant="text"
                color="error"
                @click="confirmDeleteAccount(item)"
                :disabled="deletingItemId === item.item_id"
                class="text-none"
              >
                <v-icon start>mdi-delete</v-icon>
                Remove
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn
                variant="text"
                color="primary"
                @click="syncTransactions(item)"
                :loading="syncingItemId === item.item_id"
                :disabled="deletingItemId === item.item_id"
                class="text-none"
              >
                <v-icon start>mdi-refresh</v-icon>
                Sync Transactions
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="text-h5">Remove Bank Connection</v-card-title>
        <v-card-text>
          <p>Are you sure you want to remove the connection to <strong>{{ selectedItem?.institution_name }}</strong>?</p>
          <v-radio-group v-model="deleteTransactions">
            <v-radio :value="true" label="Also delete all associated transactions"></v-radio>
            <v-radio :value="false" label="Keep all transactions in the system"></v-radio>
          </v-radio-group>
          <p class="text-caption text-medium-emphasis mt-2">
            Note: This only removes the connection from this app. It does not affect your bank account.
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" text @click="cancelDelete">Cancel</v-btn>
          <v-btn
            color="error"
            @click="deleteAccount"
            :loading="deletingInProgress"
          >
            Remove Connection
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';

export default {
  name: 'PlaidAccountsOverview',
  setup() {
    const plaidItems = ref([]);
    const itemAccounts = reactive({});
    const itemAccountsLoaded = reactive({});
    const loading = ref(true);
    const error = ref(null);
    const isPlaidConnected = ref(false);
    const syncingItemId = ref(null);
    const showDeleteDialog = ref(false);
    const selectedItem = ref(null);
    const deleteTransactions = ref(false);
    const deletingItemId = ref(null);
    const deletingInProgress = ref(false);

    // Format date for display
    const formatDate = (dateString) => {
      if (!dateString) return 'Never';
      
      try {
        const date = new Date(dateString);
        return date.toLocaleString();
      } catch (e) {
        return 'Invalid date';
      }
    };

    // Format currency for display
    const formatCurrency = (amount) => {
      if (amount == null || amount === undefined) return 'Balance unavailable';
      
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
      }).format(amount);
    };

    // Format account type for display
    const formatAccountType = (type, subtype) => {
      const formattedType = type?.charAt(0).toUpperCase() + type?.slice(1) || '';
      const formattedSubtype = subtype?.charAt(0).toUpperCase() + subtype?.slice(1) || '';
      
      if (formattedType && formattedSubtype) {
        return `${formattedType} - ${formattedSubtype}`;
      }
      return formattedSubtype || formattedType || 'Unknown account type';
    };

    // Fetch Plaid items and account information
    const fetchPlaidData = async () => {
      try {
        loading.value = true;
        error.value = null;
        
        // First, check if user has any Plaid connections
        const statusResponse = await fetch('/api/plaid_status');
        if (!statusResponse.ok) {
          throw new Error('Failed to fetch Plaid status');
        }
        
        const statusData = await statusResponse.json();
        console.log("Plaid status:", statusData);
        isPlaidConnected.value = statusData.has_plaid_connections;
        
        if (!isPlaidConnected.value) {
          loading.value = false;
          return;
        }
        
        // Get all connected items
        const itemsResponse = await fetch('/api/get_plaid_items');
        if (!itemsResponse.ok) {
          throw new Error('Failed to fetch Plaid items');
        }
        
        const itemsData = await itemsResponse.json();
        console.log("Plaid items:", itemsData);
        
        if (!itemsData.success) {
          throw new Error(itemsData.error || 'Failed to fetch Plaid items');
        }
        
        plaidItems.value = itemsData.items || [];
        
        // Initialize loading state for each item
        plaidItems.value.forEach(item => {
          itemAccountsLoaded[item.item_id] = false;
        });
        
        loading.value = false;
        
        // Fetch account details for each item (in parallel)
        const promises = plaidItems.value.map(item => fetchItemAccounts(item));
        await Promise.all(promises);
        
      } catch (err) {
        console.error('Error fetching Plaid data:', err);
        error.value = err.message;
        loading.value = false;
      }
    };

    // Fetch accounts for a specific item
    const fetchItemAccounts = async (item) => {
      try {
        console.log(`Fetching accounts for item: ${item.item_id}`);
        
        // Clear any existing accounts data
        itemAccounts[item.item_id] = [];
        itemAccountsLoaded[item.item_id] = false;
        
        // Make API request
        const response = await fetch(`/api/get_item_accounts?item_id=${item.item_id}`);
        const data = await response.json();
        
        console.log(`Account data for ${item.item_id}:`, data);
        
        if (data.success && data.accounts) {
          itemAccounts[item.item_id] = data.accounts;
        } else {
          console.warn(`No accounts found for item ${item.item_id}`);
          itemAccounts[item.item_id] = [];
        }
      } catch (err) {
        console.error(`Error fetching accounts for item ${item.item_id}:`, err);
        itemAccounts[item.item_id] = [];
      } finally {
        itemAccountsLoaded[item.item_id] = true;
      }
    };

    // Sync transactions for a specific item
    const syncTransactions = async (item) => {
      try {
        syncingItemId.value = item.item_id;
        
        const response = await fetch('/api/sync_transactions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            item_id: item.item_id
          })
        });
        
        if (!response.ok) {
          throw new Error('Failed to sync transactions');
        }
        
        const data = await response.json();
        if (data.success) {
          // Show success message
          alert(`Synced ${data.added} new transactions from ${data.institution_name}`);
          
          // Refresh the item data
          await fetchItemAccounts(item);
        } else {
          throw new Error(data.error || 'Failed to sync transactions');
        }
      } catch (err) {
        console.error('Error syncing transactions:', err);
        alert(`Error: ${err.message}`);
      } finally {
        syncingItemId.value = null;
      }
    };

    // Confirm account deletion
    const confirmDeleteAccount = (item) => {
      selectedItem.value = item;
      deleteTransactions.value = false; // Default to keeping transactions
      showDeleteDialog.value = true;
    };

    // Cancel deletion
    const cancelDelete = () => {
      showDeleteDialog.value = false;
      selectedItem.value = null;
    };

    // Delete account
    const deleteAccount = async () => {
      if (!selectedItem.value) return;
      
      try {
        deletingInProgress.value = true;
        deletingItemId.value = selectedItem.value.item_id;
        
        const response = await fetch('/api/delete_plaid_item', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            item_id: selectedItem.value.item_id,
            delete_transactions: deleteTransactions.value
          })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
          // Show success message
          alert(`Successfully removed connection to ${selectedItem.value.institution_name}`);
          
          // Close dialog and refresh data
          showDeleteDialog.value = false;
          selectedItem.value = null;
          
          // Refresh plaid data
          await fetchPlaidData();
        } else {
          throw new Error(data.error || 'Failed to delete bank connection');
        }
      } catch (err) {
        console.error('Error deleting bank connection:', err);
        alert(`Error: ${err.message}`);
      } finally {
        deletingInProgress.value = false;
        deletingItemId.value = null;
      }
    };

    // Initialize on component mount
    onMounted(fetchPlaidData);

    return {
      plaidItems,
      itemAccounts,
      itemAccountsLoaded,
      loading,
      error,
      isPlaidConnected,
      syncingItemId,
      showDeleteDialog,
      selectedItem,
      deleteTransactions,
      deletingItemId,
      deletingInProgress,
      formatDate,
      formatCurrency,
      formatAccountType,
      syncTransactions,
      confirmDeleteAccount,
      cancelDelete,
      deleteAccount
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