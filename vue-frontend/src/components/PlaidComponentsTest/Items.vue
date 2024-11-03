<template>
    <div>
      <ProductTypesContainer productType="Item Management">
        <Endpoint
          endpoint="item"
          schema="/item/get"
          description="Retrieve information about an Item, like the institution, billed products, available products, and webhook information."
        />
        <Endpoint
          endpoint="accounts"
          schema="/accounts/get"
          description="Retrieve high-level information about all accounts associated with an item."
        />
      </ProductTypesContainer>
    </div>
  </template>
  
  <script>
  import { defineComponent } from 'vue';
  
  export default defineComponent({
    name: 'Items',
  });
  </script>
  