<!-- src/components/Link.vue -->
<template>
  <button @click="openLink" :disabled="!ready">
    Launch Link
  </button>
</template>

<script>
import { defineComponent, ref, watch, onMounted } from 'vue';
import { usePlaid } from '../../composables/usePlaid';

export default defineComponent({
  name: 'Link',
  setup() {
    const { state, updateState } = usePlaid();
    const ready = ref(false);
    const isOauth = ref(false);
    let handler = null;

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
        onSuccess: async (public_token, metadata) => {
          // If the access_token is needed, send public_token to server
          const exchangePublicTokenForAccessToken = async () => {
            try {
                const response = await fetch('/api/set_access_token', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ public_token: public_token }), // Send JSON data
              });
              if (!response.ok) {
                updateState({
                  itemId: 'no item_id retrieved',
                  accessToken: 'no access_token retrieved',
                  isItemAccess: false,
                });
                return;
              }
              const data = await response.json();
              updateState({
                itemId: data.item_id,
                accessToken: data.access_token,
                isItemAccess: true,
              });
            } catch (error) {
              updateState({
                itemId: 'no item_id retrieved',
                accessToken: 'no access_token retrieved',
                isItemAccess: false,
              });
            }
          };

          if (state.isPaymentInitiation) {
            updateState({ isItemAccess: false });
          } else if (state.isCraProductsExclusively) {
            // For CRA products, access_token/public_token exchange is not needed
            updateState({ isItemAccess: false });
          } else {
            await exchangePublicTokenForAccessToken();
          }

          updateState({ linkSuccess: true });
          window.history.pushState('', '', '/');
        },
        onExit: (err, metadata) => {
          // Handle the case when a user exits Link
          console.log('User exited Link:', err, metadata);
        },
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

    onMounted(async () => {
      try {
        await loadPlaidScript();
        initializeLink();
      } catch (error) {
        console.error('Error loading Plaid script:', error);
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
    };
  },
});
</script>

<style scoped>
button {
  padding: 10px 20px;
  font-size: 16px;
}
</style>
