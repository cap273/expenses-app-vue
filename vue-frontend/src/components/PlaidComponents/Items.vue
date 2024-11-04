<!-- src/components/Items.vue -->
<template>
  <ProductTypesContainer productType="Item Management">
    <!-- Endpoint components need to be translated -->
    <Endpoint
      endpoint="item"
      :categories="itemCategories"
      schema="/item/get/"
      description="Retrieve information about an Item, like the institution, billed products, available products, and webhook information."
      :transformData="transformItemData"
    />
    <Endpoint
      endpoint="accounts"
      schema="/accounts/get"
      :categories="accountsCategories"
      description="Retrieve high-level information about all accounts associated with an item."
      :transformData="transformAccountsData"
    />
  </ProductTypesContainer>
</template>

<script>
import ProductTypesContainer from './ProductTypesContainer.vue';
// The Endpoint component needs to be translated
import Endpoint from './Endpoint.vue'; // Placeholder for now

// Import data and transformation functions
import {
  transformItemData,
  transformAccountsData,
  itemCategories,
  accountsCategories,
} from '../../utils/dataUtilities'; // Adjust the path as necessary

export default {
  name: 'Items',
  components: {
    ProductTypesContainer,
    Endpoint,
  },
  setup() {
    return {
      transformItemData,
      transformAccountsData,
      itemCategories,
      accountsCategories,
    };
  },
};
</script>

<style scoped>
/* Add any necessary styling here */
</style>
