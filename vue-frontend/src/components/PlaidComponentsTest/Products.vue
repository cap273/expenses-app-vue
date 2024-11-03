<template>
    <div>
      <ProductTypesContainer productType="Products">
        <Endpoint
          v-if="products.includes('payment_initiation')"
          endpoint="payment"
          name="Payment"
          description="Retrieve information about your latest payment."
        />
        <Endpoint
          v-if="products.includes('auth')"
          endpoint="auth"
          name="Auth"
          description="Retrieve account and routing numbers for checking and savings accounts."
        />
        <!-- More Endpoints according to conditions -->
      </ProductTypesContainer>
    </div>
  </template>
  
  <script>
  import { defineComponent } from 'vue';
  
  export default defineComponent({
    name: 'Products',
    props: ['products', 'isCraProductsExclusively'],
  });
  </script>
  