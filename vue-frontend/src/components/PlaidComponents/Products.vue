<!-- src/components/Products.vue -->
<template>
  <ProductTypesContainer productType="Products">
    <Endpoint v-if="products.includes('transactions')" endpoint="transactions" />
    <Endpoint v-if="products.includes('balance')" endpoint="balance" />
  </ProductTypesContainer>
</template>

<script>
import { computed } from 'vue';
import ProductTypesContainer from './ProductTypesContainer.vue';
import Endpoint from './Endpoint.vue';
import { usePlaid } from '../../composables/usePlaid';

export default {
  name: 'Products',
  components: {
    ProductTypesContainer,
    Endpoint,
  },
  setup() {
    const { state } = usePlaid();
    const products = computed(() => state.products);

    return {
      products,
    };
  },
};
</script>

<style scoped>
/* Add any necessary styling here */
</style>
