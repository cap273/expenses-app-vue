<template>
  <v-app-bar app>
    <v-row no-gutters>
      <!-- Left-most Column -->
      <v-col cols="2" sm="3" class="d-flex justify-center align-center">
        <v-toolbar-title>
          <v-img :src="placeholderLogo" @click="$router.push('/')" class="clickable"></v-img>
        </v-toolbar-title>
      </v-col>

      <!-- Middle Column -->
      <v-col cols="6" sm="4" class="d-flex align-center">
        <template v-if="!globalState.authenticated">
          <v-btn text href="#features" class="hidden-xs-only first-nav-button">Features</v-btn>
          <v-btn text href="#pricing" class="hidden-xs-only">Pricing</v-btn>
        </template>
        <template v-else>
          <v-btn text :class="[getButtonClass('InputExpenses'), 'first-nav-button']" to="/input_expenses">Input Expenses</v-btn>
          <v-btn text :class="getButtonClass('ViewExpenses')" to="/view_expenses">View Expenses</v-btn>
        </template>
      </v-col>

      <!-- Right-most Column -->
      <v-col cols="4" sm="5" class="d-flex justify-center align-center">
        <template v-if="!globalState.authenticated">
          <v-btn text to="/login" class="mr-1">Log In</v-btn>
          <v-btn outlined to="/signup" class="mr-4">Sign Up</v-btn>
        </template>
        <template v-else>
          <v-btn text class="d-flex align-center">
            <v-icon left>mdi-account</v-icon>
            {{ globalState.username }}
            <v-menu activator="parent" offset-y>
              <v-list>
                <v-list-item link :to="{ name: 'Profile' }">
                  <v-list-item-title>Profile</v-list-item-title>
                </v-list-item>
                <v-list-item @click="logout">
                  <v-list-item-title>Log Out</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-btn>
        </template>
      </v-col>
    </v-row>
  </v-app-bar>
</template>


<script>
import { globalState } from '@/main.js';
import placeholderLogo from '@/assets/placeholder-logo.png';


export default {
  data() {
    return {
      placeholderLogo,
      globalState
    };
  },
  methods: {
    getButtonClass(routeName) {
    return {
      'nav-button': true,
      'light-blue': this.$route.name !== routeName,
      'dark-blue': this.$route.name === routeName
    };
  },
    logout() {
      fetch('/api/logout')
        .then(() => {
          // Clear global state
          globalState.authenticated = false;
          globalState.username = null;
          globalState.display_name = null;
          this.$router.push('/'); // Redirect to the main page
        });
    }
  }
};
</script>

<style>

.first-nav-button {
  margin-left: 15px;
}

.clickable {
  cursor: pointer;
}

.nav-button {
  color: grey;
  background-color: transparent;
}

.nav-button:hover {
  background-color: lightgrey;
}

.light-blue {
  color: lightblue;
}

.dark-blue {
  color: darkblue;
}
</style>
