<template>
  <v-card class="mt-6" elevation="1">
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
          <v-card elevation="2">
            <v-card-item>
              <v-card-title>{{ item.institution_name }}</v-card-title>
              <v-card-subtitle v-if="item.last_synced">
                Last synced: {{ formatDate(item.last_synced) }}
              </v-card-subtitle>
            </v-card-item>
            <v-card-text>
              <div v-if="itemAccountsLoaded[item.item_id]">
                <div
                  v-if="itemAccounts[item.item_id] && itemAccounts[item.item_id].length"
                >
                  <div
                    v-for="account in itemAccounts[item.item_id]"
                    :key="account.account_id"
                    class="mb-3"
                  >
                    <div class="d-flex justify-space-between align-center">
                      <div>{{ account.name }}</div>
                      <div class="font-weight-medium">
                        {{ formatCurrency(account.balances.available || account.balances.current) }}
                      </div>
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
                <v-progress-circular
                  indeterminate
                  size="24"
                  width="2"
                  color="primary"
                ></v-progress-circular>
                <p class="mt-2">Loading accounts...</p>
              </div>
            </v-card-text>
            <v-card-actions>
              <v-btn
                variant="text"
                color="error"
                @click="confirmDeleteAccount(item)"
                :disabled="deletingItemId === item.item_id"
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
              >
                <v-icon start>mdi-refresh</v-icon>
                Sync
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
          <p>
            Are you sure you want to remove the connection to
            <strong>{{ selectedItem?.institution_name }}</strong>?
          </p>
          <v-radio-group v-model="deleteTransactions">
            <v-radio :value="true" label="Also delete all associated transactions" />
            <v-radio :value="false" label="Keep all transactions in the system" />
          </v-radio-group>
          <p class="text-caption text-medium-emphasis mt-2">
            Note: This only removes the connection from this app. It does not affect
            your bank account.
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
import { ref, reactive, onMounted, computed, toRefs } from 'vue';
import { formatDate } from '@/utils/dateUtils';
import { formatCurrency } from '@/utils/formatUtils';


export default {
  name: 'PlaidAccountsOverview',
  emits: ['accounts-fetched'],
  setup(props, { emit }) {
    const plaidItems = ref([]);
    const itemAccounts = reactive({});
    const itemAccountsLoaded = reactive({});
    const loading = ref(true);
    const error = ref(null);
    const isPlaidConnected = ref(false);
    const syncingItemId = ref(null);

    // For delete workflow
    const showDeleteDialog = ref(false);
    const selectedItem = ref(null);
    const deleteTransactions = ref(false);
    const deletingItemId = ref(null);
    const deletingInProgress = ref(false);

    // We'll track the total of all accounts here,
    // and then emit it back to the parent
    const totalBalance = ref(0);

    // Format account type
    const formatAccountType = (type, subtype) => {
      if (!type && !subtype) return 'Unknown';
      const t = type ? type[0].toUpperCase() + type.slice(1) : '';
      const st = subtype ? subtype[0].toUpperCase() + subtype.slice(1) : '';
      if (t && st) return `${t} - ${st}`;
      return t || st || 'Unknown';
    };

    // Fetch all Plaid data (items + accounts)
    const fetchPlaidData = async () => {
      try {
        loading.value = true;
        error.value = null;

        // Check if user has any Plaid connections
        const statusResponse = await fetch('/api/plaid_status');
        if (!statusResponse.ok) {
          throw new Error('Failed to fetch Plaid status');
        }
        const statusData = await statusResponse.json();
        isPlaidConnected.value = statusData.has_plaid_connections;

        if (!isPlaidConnected.value) {
          loading.value = false;
          // No connected accounts, so totalBalance = 0
          emit('accounts-fetched', 0);
          return;
        }

        // Fetch the Plaid items
        const itemsResponse = await fetch('/api/get_plaid_items');
        const itemsData = await itemsResponse.json();
        if (!itemsData.success) {
          throw new Error(itemsData.error || 'Failed to fetch Plaid items');
        }
        plaidItems.value = itemsData.items || [];

        // Initialize
        plaidItems.value.forEach((item) => {
          itemAccounts[item.item_id] = [];
          itemAccountsLoaded[item.item_id] = false;
        });

        loading.value = false;

        // Get accounts for each item in parallel
        const promises = plaidItems.value.map((item) => fetchItemAccounts(item));
        await Promise.all(promises);

        // Once all accounts are fetched, recalc the total
        recalcTotalBalance();
      } catch (err) {
        console.error('Error fetching Plaid data:', err);
        error.value = err.message;
        loading.value = false;
        emit('accounts-fetched', 0);
      }
    };

    // Fetch accounts for a specific item
    const fetchItemAccounts = async (item) => {
      try {
        const response = await fetch(`/api/get_item_accounts?item_id=${item.item_id}`);
        const data = await response.json();
        if (data.success && data.accounts) {
          itemAccounts[item.item_id] = data.accounts;
        } else {
          itemAccounts[item.item_id] = [];
        }
      } catch (err) {
        console.error(`Error fetching accounts for item ${item.item_id}:`, err);
        itemAccounts[item.item_id] = [];
      } finally {
        itemAccountsLoaded[item.item_id] = true;
      }
    };

    // Recalculate total balance from all item accounts
    const recalcTotalBalance = () => {
      let sum = 0;
      plaidItems.value.forEach((item) => {
        const accounts = itemAccounts[item.item_id] || [];
        accounts.forEach((acct) => {
          const bal = acct.balances.available ?? acct.balances.current ?? 0;
          sum += bal;
        });
      });
      totalBalance.value = sum;
      // Emit up to parent
      emit('accounts-fetched', totalBalance.value);
    };

    // Sync transactions for an item
    const syncTransactions = async (item) => {
      try {
        syncingItemId.value = item.item_id;
        const response = await fetch('/api/sync_transactions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ item_id: item.item_id }),
        });
        if (!response.ok) {
          throw new Error('Failed to sync transactions');
        }
        const data = await response.json();
        if (!data.success) {
          throw new Error(data.error || 'Failed to sync transactions');
        }
        // Show success
        alert(`Synced ${data.added} new transactions from ${data.institution_name}`);
        // Refresh the item’s accounts
        await fetchItemAccounts(item);
        // Recalc total
        recalcTotalBalance();
      } catch (err) {
        console.error('Error syncing transactions:', err);
        alert(`Error: ${err.message}`);
      } finally {
        syncingItemId.value = null;
      }
    };

    // Confirm delete
    const confirmDeleteAccount = (item) => {
      selectedItem.value = item;
      deleteTransactions.value = false;
      showDeleteDialog.value = true;
    };

    // Cancel
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
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            item_id: selectedItem.value.item_id,
            delete_transactions: deleteTransactions.value,
          }),
        });
        const data = await response.json();

        if (!response.ok || !data.success) {
          throw new Error(data.error || 'Failed to delete bank connection');
        }

        alert(`Successfully removed connection to ${selectedItem.value.institution_name}`);
        showDeleteDialog.value = false;
        selectedItem.value = null;

        // Refresh everything
        await fetchPlaidData();
      } catch (err) {
        console.error('Error deleting bank connection:', err);
        alert(`Error: ${err.message}`);
      } finally {
        deletingInProgress.value = false;
        deletingItemId.value = null;
      }
    };

    onMounted(fetchPlaidData);

    return {
      // Data / Refs
      plaidItems,
      itemAccounts,
      itemAccountsLoaded,
      loading,
      error,
      isPlaidConnected,
      syncingItemId,
      totalBalance,
      showDeleteDialog,
      selectedItem,
      deleteTransactions,
      deletingItemId,
      deletingInProgress,

      // Methods
      formatDate,
      formatCurrency,
      formatAccountType,
      fetchPlaidData,
      fetchItemAccounts,
      syncTransactions,
      confirmDeleteAccount,
      cancelDelete,
      deleteAccount,
    };
  },
};
</script>

<style scoped>
.v-card {
  margin-bottom: 16px;
}
</style>