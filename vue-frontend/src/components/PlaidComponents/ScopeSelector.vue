<!-- src/components/PlaidComponents/ScopeSelector.vue -->
<template>
    <v-dialog v-model="dialogOpen" max-width="500px" persistent>
      <v-card>
        <v-card-title class="headline">Select a Scope</v-card-title>
        <v-card-text>
          <p class="mb-4">
            Choose which scope to associate with this bank account. 
            All transactions will be imported into the selected scope.
          </p>
          <v-select
            v-model="selectedScope"
            :items="scopes"
            item-title="display_name"
            item-value="id"
            label="Select Scope"
            return-object
            :loading="loading"
            :disabled="loading"
            :error-messages="error ? [error] : []"
          ></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn 
            color="primary" 
            @click="confirmScope" 
            :disabled="!selectedScope || loading"
            :loading="confirmLoading"
          >
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script>
  import { ref, computed, watch } from 'vue';
  
  export default {
    name: 'ScopeSelector',
    props: {
      show: {
        type: Boolean,
        default: false
      },
      publicToken: {
        type: String,
        required: true
      }
    },
    emits: ['close', 'success', 'error'],
    setup(props, { emit }) {
      const dialogOpen = ref(false);
      const scopes = ref([]);
      const selectedScope = ref(null);
      const loading = ref(false);
      const confirmLoading = ref(false);
      const error = ref('');
  
      // Watch for show prop changes
      watch(() => props.show, (newVal) => {
        dialogOpen.value = newVal;
        if (newVal) {
          fetchScopes();
        }
      });
  
      // Watch for dialog close
      watch(dialogOpen, (newVal) => {
        if (!newVal && props.show) {
          emit('close');
        }
      });
  
      // Watch for public token changes
      watch(() => props.publicToken, (newToken) => {
        console.log('Public token updated:', newToken);
      });
  
      // Fetch available scopes for the user
      const fetchScopes = async () => {
        try {
          loading.value = true;
          error.value = '';
          
          const response = await fetch('/api/get_available_scopes');
          if (!response.ok) {
            throw new Error('Failed to fetch scopes');
          }
          
          const data = await response.json();
          console.log('Fetched scopes:', data);
          
          if (data.success) {
            // Transform the scopes to include a display name
            scopes.value = data.scopes.map(scope => ({
              id: scope.id,
              name: scope.name,
              type: scope.type,
              access_type: scope.access_type,
              display_name: `${scope.name} (${scope.type})`
            }));
            
            // If there's only one scope, select it automatically
            if (scopes.value.length === 1) {
              selectedScope.value = scopes.value[0];
            }
          } else {
            throw new Error(data.error || 'Failed to fetch scopes');
          }
        } catch (err) {
          console.error('Error fetching scopes:', err);
          error.value = err.message;
        } finally {
          loading.value = false;
        }
      };
  
      // Submit the selected scope with the public token
      const confirmScope = async () => {
        if (!selectedScope.value) {
          error.value = 'Please select a scope';
          return;
        }
        
        if (!props.publicToken) {
          error.value = 'Missing public token';
          return;
        }
        
        try {
          confirmLoading.value = true;
          error.value = '';
          
          console.log('Sending token exchange request with:', {
            public_token: props.publicToken,
            scope_id: selectedScope.value.id
          });
          
          const response = await fetch('/api/set_access_token', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              public_token: props.publicToken,
              scope_id: selectedScope.value.id
            })
          });
          
          const data = await response.json();
          console.log('Token exchange response:', data);
          
          if (data.success) {
            emit('success', {
              item_id: data.item_id,
              access_token: data.access_token,
              institution_name: data.institution_name,
              scope_id: data.scope_id
            });
            dialogOpen.value = false;
          } else {
            throw new Error(data.error || 'Failed to exchange token');
          }
        } catch (err) {
          console.error('Error setting access token:', err);
          error.value = err.message;
          emit('error', err.message);
        } finally {
          confirmLoading.value = false;
        }
      };
  
      return {
        dialogOpen,
        scopes,
        selectedScope,
        loading,
        confirmLoading,
        error,
        fetchScopes,
        confirmScope
      };
    }
  }
  </script>