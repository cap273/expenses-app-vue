<!-- src/views/PlaidDashboard.vue -->
<template>
  <div class="App">
    <div class="container">
      <Header @link-success="onLinkSuccess" />
      <div v-if="state.linkSuccess">
        <p>Link was successful!</p>
        <p v-if="state.itemId">Item ID: {{ state.itemId }}</p>
        <Products />
        <Items v-if="!state.isPaymentInitiation && state.itemId" />
      </div>
      <div v-else>
        <p>Link not yet successful.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, onMounted, ref, watch } from 'vue';
import { usePlaid } from '../composables/usePlaid';
import Header from '../components/PlaidComponents/Header.vue';
import Products from '../components/PlaidComponents/Products.vue';
import Items from '../components/PlaidComponents/Items.vue';

export default defineComponent({
  name: 'PlaidDashboard',
  components: {
    Header,
    Products,
    Items,
  },
  emits: ['connection-success'],
  setup(props, { emit }) {
    const { state } = usePlaid();
    const connectionProcessed = ref(false);

    // Handle link success event from Header component
    const onLinkSuccess = (data) => {
      console.log('Link success received in PlaidDashboard:', data);
      emit('connection-success', {
        institution_name: data.institution_name || 'your bank',
        scope_id: data.scope_id || state.scopeId,
        item_id: data.item_id || state.itemId
      });
    };

    // Also watch the state to catch success events
    watch(
      () => state.linkSuccess,
      (newVal, oldVal) => {
        if (newVal === true && oldVal === false && !connectionProcessed.value && state.itemId) {
          // This is a new successful connection
          connectionProcessed.value = true;
          
          // Fetch additional information if needed
          fetchInstitutionName(state.itemId).then(institutionName => {
            emit('connection-success', {
              institution_name: institutionName || 'your bank',
              scope_id: state.scopeId,
              item_id: state.itemId
            });
          });
        }
      }
    );

    // Helper to fetch institution name if not provided
    const fetchInstitutionName = async (itemId) => {
      try {
        const response = await fetch(`/api/get_plaid_items`);
        const data = await response.json();
        if (data.success && data.items) {
          const item = data.items.find(i => i.item_id === itemId);
          return item ? item.institution_name : null;
        }
      } catch (error) {
        console.error('Error fetching institution name:', error);
      }
      return null;
    };

    return {
      state,
      onLinkSuccess
    };
  },
});
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 700px; /* Adjusted from 70 * $unit */
  max-width: 1200px; /* Adjusted from 120 * $unit */
  margin: 0 auto;
}
</style>