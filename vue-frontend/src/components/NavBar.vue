<template>
    <v-app-bar app>
      <!-- ... other navigation content ... -->
      <div v-if="username">Welcome, {{ username }}</div>
    </v-app-bar>
  </template>
  
  <script>
  export default {
    props: ['username']
  };
  </script>