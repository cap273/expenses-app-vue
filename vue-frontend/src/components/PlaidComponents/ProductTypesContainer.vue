<!-- src/components/ProductTypesContainer.vue -->
<template>
    <div class="container">
      <h4 class="header">{{ productType }}</h4>
      <slot></slot>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ProductTypesContainer',
    props: {
      productType: {
        type: String,
        required: true,
      },
    },
  };
  </script>
  
  <style scoped>
  .container {
    width: 100%;
    border: 1px solid #e0e0e0; /* Replacing $black200 */
    border-radius: 2px;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.2); /* Replacing $shadow-small */
    margin: 0 0 30px 0; /* Replacing '3 * $unit' with '30px' */
  }
  
  .header {
    width: 100%;
    border-bottom: 0px;
    height: 130px; /* Replacing '13 * $unit' with '130px' */
    font-weight: 800;
    padding-top: 50px; /* Replacing '5 * $unit' with '50px' */
    padding-left: 50px; /* Replacing '5 * $unit' with '50px' */
    margin-top: 0;
    margin-bottom: 0;
  }
  </style>
  