<!-- src/views/PlaidDashboard.vue -->
<template>
  <div class="App">
    <div class="container">
      <Header />
      <div v-if="state.linkSuccess">
        <p>Link was successful!</p>
        <p>Item ID: {{ state.itemId }}</p>
        <Products />
        <Items v-if="!state.isPaymentInitiation && state.itemId" />
      </div>
      <div v-else>
        <p>Link not yet successful.</p>
      </div>
    </div>
  </div>
</template>

<!--
<template>
  <div class="App">
    <div class="container">
      <Header />
      <div v-if="state.linkSuccess">
        <Products />
        <Items v-if="!state.isPaymentInitiation && state.itemId" />
      </div>
    </div>
  </div>
</template>
-->

<script>
import { defineComponent, onMounted } from 'vue';
import { usePlaid } from '../composables/usePlaid';
// The following components need to be translated from React to Vue
// Currently, they are placeholders
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
  setup() {
    const { state } = usePlaid();

    // If you need to perform additional setup, you can use onMounted here
    onMounted(() => {
      // Additional setup if necessary
    });

    return {
      state,
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
