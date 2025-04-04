<!-- src/components/PlaidComponents/Link.vue -->
<template>
  <div>
    <button @click="openLink" :disabled="!ready" class="plaid-link-button">
      Launch Link
    </button>
    
    <!-- Scope Selector Dialog -->
    <ScopeSelector
      :show="showScopeSelector"
      :public-token="publicTokenValue"
      @success="handleLinkSuccess"
      @error="handleLinkError"
      @close="showScopeSelector = false"
    />
  </div>
</template>

<script>
import { defineComponent, ref, watch, onMounted } from 'vue';
import { usePlaid, setScopeId } from '../../composables/usePlaid';
import ScopeSelector from './ScopeSelector.vue';

export default defineComponent({
  name: 'Link',
  components: {
    ScopeSelector
  },
  emits: ['link-success', 'link-error'],
  setup(props, { emit }) {
    const { state, updateState } = usePlaid();
    const ready = ref(false);
    const isOauth = ref(false);
    const showScopeSelector = ref(false);
    const publicTokenValue = ref('');
    let handler = null;
    
    // Store institution data from Public Token exchange
    const institutionData = ref({
      institution_name: '',
      institution_id: ''
    });

    const loadPlaidScript = () => {
      return new Promise((resolve, reject) => {
        if (document.getElementById('plaid-link-script')) {
          // If the script is already loaded, resolve when window.Plaid is available
          if (typeof window.Plaid !== 'undefined') {
            resolve();
          } else {
            // Wait until window.Plaid is defined
            const interval = setInterval(() => {
              if (typeof window.Plaid !== 'undefined') {
                clearInterval(interval);
                resolve();
              }
            }, 100);
          }
          return;
        }
        const script = document.createElement('script');
        script.id = 'plaid-link-script';
        script.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
        script.onload = () => {
          // Wait until window.Plaid is defined
          if (typeof window.Plaid !== 'undefined') {
            resolve();
          } else {
            const interval = setInterval(() => {
              if (typeof window.Plaid !== 'undefined') {
                clearInterval(interval);
                resolve();
              }
            }, 100);
          }
        };
        script.onerror = () => reject(new Error('Failed to load Plaid Link script'));
        document.head.appendChild(script);
      });
    };

    const initializeLink = () => {
      if (!state.linkToken) {
        console.error('linkToken is not available');
        return;
      }

      if (typeof window.Plaid === 'undefined') {
        console.error('window.Plaid is undefined in initializeLink');
        return;
      }

      const config = {
        token: state.linkToken,
        onSuccess: (public_token, metadata) => {
          // Store the public token and show scope selector
          console.log('Plaid Link success, public token:', public_token);
          console.log('Plaid Link metadata:', metadata);
          
          // Store institution data from metadata
          if (metadata.institution) {
            institutionData.value = {
              institution_name: metadata.institution.name,
              institution_id: metadata.institution.institution_id
            };
          }
          
          publicTokenValue.value = public_token;
          showScopeSelector.value = true;
        },
        onExit: (err, metadata) => {
          // Handle the case when a user exits Link
          console.log('User exited Link:', err, metadata);
          if (err) {
            emit('link-error', err);
          }
        },
        onLoad: () => {
          console.log('Plaid Link loaded');
        },
        onEvent: (eventName, metadata) => {
          console.log('Plaid Link event:', eventName, metadata);
        }
      };

      if (window.location.href.includes('?oauth_state_id=')) {
        config.receivedRedirectUri = window.location.href;
        isOauth.value = true;
      }

      handler = window.Plaid.create(config);
      ready.value = true;

      if (isOauth.value) {
        handler.open();
      }
    };

    const openLink = () => {
      if (ready.value && handler) {
        handler.open();
      } else {
        console.error('Plaid Link is not ready');
      }
    };
    
    const handleLinkSuccess = (data) => {
      console.log('Link success with data:', data);
      updateState({
        itemId: data.item_id,
        accessToken: data.access_token,
        isItemAccess: true,
        linkSuccess: true
      });

      // Set the scope ID in the Plaid state
      setScopeId(data.scope_id);
      
      // Emit an event with all relevant data
      emit('link-success', {
        item_id: data.item_id,
        access_token: data.access_token,
        institution_name: data.institution_name || institutionData.value.institution_name,
        institution_id: data.institution_id || institutionData.value.institution_id,
        scope_id: data.scope_id
      });
      
      showScopeSelector.value = false;
      window.history.pushState('', '', '/');
    };
    
    const handleLinkError = (error) => {
      console.error('Link error:', error);
      emit('link-error', error);
      showScopeSelector.value = false;
    };

    onMounted(async () => {
      try {
        await loadPlaidScript();
        initializeLink();
      } catch (error) {
        console.error('Error loading Plaid script:', error);
        emit('link-error', error);
      }
    });

    watch(
      () => state.linkToken,
      (newLinkToken) => {
        if (newLinkToken && !handler) {
          initializeLink();
        }
      }
    );

    return {
      openLink,
      ready,
      showScopeSelector,
      publicTokenValue,
      handleLinkSuccess,
      handleLinkError
    };
  },
});
</script>

<style scoped>
.plaid-link-button {
  padding: 10px 20px;
  font-size: 16px;
  background-color: #2c7cff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.plaid-link-button:hover {
  background-color: #1b5dbd;
}

.plaid-link-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>