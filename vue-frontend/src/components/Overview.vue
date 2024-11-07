<template>
    <div class="page-background">
      <v-container class="content-container">
        <div class="content-box">
          <h2 class="text-h4 mb-6">Overview</h2>
          
          <!-- Summary Cards Row -->
          <v-row class="mb-6">
            <v-col cols="12" md="4">
              <v-card>
                <v-card-item>
                  <v-card-title>This Month's Spending</v-card-title>
                  <div class="text-h5 mt-2">$2,450.33</div>
                </v-card-item>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-card>
                <v-card-item>
                  <v-card-title>Most Spent On</v-card-title>
                  <div class="text-h5 mt-2">Groceries</div>
                </v-card-item>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-card>
                <v-card-item>
                  <v-card-title>Active Scopes</v-card-title>
                  <div class="text-h5 mt-2">3</div>
                </v-card-item>
              </v-card>
            </v-col>
          </v-row>
  
          <!-- Plaid Accounts Section -->
          <PlaidAccountsOverview />
        </div>
      </v-container>
    </div>
  </template>
  
  <script>
  import PlaidAccountsOverview from './PlaidComponents/PlaidAccountsOverview.vue';
  
  export default {
    name: 'Overview',
    components: {
      PlaidAccountsOverview,
    }
  };
  </script>
  
  <style scoped>
  /* Add any component-specific styles here */
  </style>