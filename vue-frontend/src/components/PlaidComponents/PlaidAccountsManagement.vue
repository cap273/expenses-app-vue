<!-- src/components/PlaidComponents/PlaidAccountsManagement.vue -->
<template>
    <v-card variant="outlined" class="mb-4">
      <v-card-title class="d-flex justify-space-between align-center">
        <span>Connected Bank Accounts</span>
        <v-btn
          color="primary"
          variant="text"
          size="small"
          prepend-icon="mdi-plus"
          @click="openPlaidLink"
          :loading="loadingLink"
        >
          Connect New Account
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-alert
          v-if="errorMessage"
          type="error"
          variant="tonal"
          closable
          @click:close="errorMessage = ''"
          class="mb-4"
        >
          {{ errorMessage }}
        </v-alert>
        
        <v-alert
          v-if="successMessage"
          type="success"
          variant="tonal"
          closable
          @click:close="successMessage = ''"
          class="mb-4"
        >
          {{ successMessage }}
        </v-alert>
        
        <!-- Loading state -->
        <div v-if="loading" class="d-flex justify-center py-4">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>
        
        <!-- No connected accounts -->
        <div v-else-if="!plaidItems || plaidItems.length === 0" class="text-center py-4">
          <p class="text-body-1 text-medium-emphasis">
            No accounts connected yet. Click "Connect New Account" to link your bank.
          </p>
        </div>
        
        <!-- Connected accounts list -->
        <div v-else>
          <v-list>
            <v-list-item
              v-for="item in plaidItems"
              :key="item.item_id"
              :title="item.institution_name"
              :subtitle="`${item.scope_name} • Last synced: ${formatLastSynced(item.last_synced)}`"
            >
              <template v-slot:prepend>
                <v-avatar color="primary" variant="tonal">
                  <v-icon>mdi-bank</v-icon>
                </v-avatar>
              </template>
              
              <template v-slot:append>
                <v-btn
                  icon="mdi-sync"
                  variant="text"
                  size="small"
                  :loading="syncingItemId === item.item_id"
                  @click="syncTransactions(item)"
                  :disabled="loading"
                >
                </v-btn>
              </template>
            </v-list-item>
          </v-list>
        </div>
      </v-card-text>
      
      <v-divider v-if="plaidItems && plaidItems.length > 0"></v-divider>
      
      <v-card-actions v-if="plaidItems && plaidItems.length > 0" class="justify-center">
        <v-btn
          color="primary"
          variant="outlined"
          prepend-icon="mdi-sync"
          size="small"
          :loading="syncingAll"
          @click="syncAllTransactions"
        >
          Sync All Accounts
        </v-btn>
      </v-card-actions>
    </v-card>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { usePlaid } from '../../composables/usePlaid';
  
  export default {
    name: 'PlaidAccountsManagement',
    setup() {
      const { generateToken } = usePlaid();
      const plaidItems = ref([]);
      const loading = ref(true);
      const loadingLink = ref(false);
      const errorMessage = ref('');
      const successMessage = ref('');
      const syncingItemId = ref(null);
      const syncingAll = ref(false);
  
      // Format the last synced date
      const formatLastSynced = (dateString) => {
        if (!dateString) return 'Never';
        
        try {
          const date = new Date(dateString);
          return date.toLocaleString();
        } catch (e) {
          return 'Invalid date';
        }
      };
  
      // Fetch the user's connected Plaid items
      const fetchPlaidItems = async () => {
        try {
          loading.value = true;
          errorMessage.value = '';
          
          const response = await fetch('/api/get_plaid_items');
          if (!response.ok) {
            throw new Error('Failed to fetch Plaid items');
          }
          
          const data = await response.json();
          console.log('Plaid items response:', data);
          
          if (data.success) {
            plaidItems.value = data.items || [];
          } else {
            throw new Error(data.error || 'Failed to fetch Plaid items');
          }
        } catch (err) {
          console.error('Error fetching Plaid items:', err);
          errorMessage.value = err.message;
        } finally {
          loading.value = false;
        }
      };
  
      // Open Plaid Link to connect a new account
      const openPlaidLink = async () => {
        try {
          loadingLink.value = true;
          errorMessage.value = '';
          
          // Generate a new link token
          await generateToken();
          
          // Create the Plaid Link handler
          window.linkHandler = window.Plaid.create({
            token: localStorage.getItem('link_token'),
            onSuccess: (public_token, metadata) => {
              console.log('Plaid Link onSuccess', metadata);
              // After successful linking, show scope selector
              showScopeSelector(public_token);
            },
            onExit: (err, metadata) => {
              // Handle exit
              loadingLink.value = false;
              if (err) {
                errorMessage.value = `Link exit error: ${err.error_message}`;
              }
            },
            onLoad: () => {
              // Link loaded
              loadingLink.value = false;
            },
            onEvent: (eventName, metadata) => {
              // Optional event handling
              console.log('Plaid Link event:', eventName, metadata);
            },
            receivedRedirectUri: null,
          });
          
          // Open Plaid Link
          window.linkHandler.open();
        } catch (err) {
          console.error('Error opening Plaid Link:', err);
          errorMessage.value = err.message;
          loadingLink.value = false;
        }
      };
  
      // Show scope selector
      const showScopeSelector = async (publicToken) => {
        try {
          // First, get available scopes
          const scopesResponse = await fetch('/api/get_available_scopes');
          if (!scopesResponse.ok) {
            throw new Error('Failed to fetch available scopes');
          }
          
          const scopesData = await scopesResponse.json();
          if (!scopesData.success) {
            throw new Error(scopesData.error || 'Failed to fetch available scopes');
          }
          
          // Create a formatted list of scopes for the selection dialog
          const scopes = scopesData.scopes.map(scope => ({
            text: `${scope.name} (${scope.type})`,
            value: scope.id
          }));
          
          if (scopes.length === 0) {
            throw new Error('No available scopes found');
          }
          
          // If there's only one scope, use it automatically
          let selectedScopeId;
          if (scopes.length === 1) {
            selectedScopeId = scopes[0].value;
          } else {
            // Show scope selection dialog
            // This is a simple implementation - you may want to use a more sophisticated dialog
            const scopeOptions = scopes.map(s => `${s.text} (${s.value})`).join('\n');
            const selectedIndex = window.prompt(`Select a scope by number (1-${scopes.length}):\n${scopeOptions}`);
            
            if (!selectedIndex || isNaN(selectedIndex) || selectedIndex < 1 || selectedIndex > scopes.length) {
              throw new Error('Invalid scope selection');
            }
            
            selectedScopeId = scopes[selectedIndex - 1].value;
          }
          
          // Now exchange the token with the selected scope
          await exchangeToken(publicToken, selectedScopeId);
          
        } catch (err) {
          console.error('Error selecting scope:', err);
          errorMessage.value = err.message;
        }
      };
  
      // Exchange the public token for an access token
      const exchangeToken = async (publicToken, scopeId) => {
        try {
          const response = await fetch('/api/set_access_token', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              public_token: publicToken,
              scope_id: scopeId
            })
          });
          
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Token exchange failed');
          }
          
          const data = await response.json();
          console.log('Token exchange response:', data);
          
          if (data.success) {
            successMessage.value = `Successfully connected ${data.institution_name}`;
            fetchPlaidItems(); // Refresh the list
          } else {
            throw new Error(data.error || 'Token exchange failed');
          }
        } catch (err) {
          console.error('Error exchanging token:', err);
          errorMessage.value = err.message;
        }
      };
  
      // Sync transactions for a specific Plaid item
      const syncTransactions = async (item) => {
        try {
          syncingItemId.value = item.item_id;
          errorMessage.value = '';
          
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
          console.log('Sync response:', data);
          
          if (data.success) {
            successMessage.value = `Synced ${data.added} new transactions from ${data.institution_name}`;
            fetchPlaidItems(); // Refresh the list to update last synced time
          } else {
            throw new Error(data.error || 'Failed to sync transactions');
          }
        } catch (err) {
          console.error('Error syncing transactions:', err);
          errorMessage.value = err.message;
        } finally {
          syncingItemId.value = null;
        }
      };
  
      // Sync all Plaid items
      const syncAllTransactions = async () => {
        if (!plaidItems.value || plaidItems.value.length === 0) return;
        
        try {
          syncingAll.value = true;
          errorMessage.value = '';
          let totalAdded = 0;
          
          for (const item of plaidItems.value) {
            try {
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
                console.error(`Failed to sync transactions for ${item.institution_name}`);
                continue;
              }
              
              const data = await response.json();
              if (data.success) {
                totalAdded += data.added;
              }
            } catch (innerErr) {
              console.error(`Error syncing ${item.institution_name}:`, innerErr);
            }
          }
          
          successMessage.value = `Synced ${totalAdded} new transactions from all accounts`;
          fetchPlaidItems(); // Refresh the list
        } catch (err) {
          console.error('Error syncing all transactions:', err);
          errorMessage.value = err.message;
        } finally {
          syncingAll.value = false;
        }
      };
  
      // Load data on component mount
      onMounted(() => {
        // Load the Plaid Link script if it doesn't exist
        if (typeof window !== 'undefined' && !window.Plaid) {
          const script = document.createElement('script');
          script.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
          script.onload = fetchPlaidItems;
          document.head.appendChild(script);
        } else {
          fetchPlaidItems();
        }
      });
  
      return {
        plaidItems,
        loading,
        loadingLink,
        errorMessage,
        successMessage,
        syncingItemId,
        syncingAll,
        formatLastSynced,
        openPlaidLink,
        syncTransactions,
        syncAllTransactions
      };
    }
  };
  </script>