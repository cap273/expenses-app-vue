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
      <v-col cols="6" sm="4" class="d-flex justify-start align-center">
        <!-- Hamburger Menu Icon (Visible only on small screens) -->
        <v-btn icon class="d-sm-none" @click="toggleDrawer" style="align-self: center;">
          <v-icon>mdi-menu</v-icon>
        </v-btn>

        <!-- Regular Buttons for Large Screens (Middle Column) -->
        <div class="d-none d-sm-flex flex-grow-1 align-items-center justify-start">
          <template v-if="!globalState.authenticated">
            <v-btn text href="#features" class="first-nav-button">Features</v-btn>
            <v-btn text href="#pricing">Pricing</v-btn>
          </template>
          <template v-else>
            <v-btn text :class="[getButtonClass('InputExpenses'), 'first-middle-nav-button']" to="/input_expenses">Input Expenses</v-btn>
            <v-btn text :class="getButtonClass('ViewExpenses')" to="/view_expenses">View Expenses</v-btn>
          </template>
        </div>
      </v-col>

      <!-- Right-most Column -->
      <v-col cols="4" sm="5" class="d-flex justify-center align-center">
        <template v-if="!globalState.authenticated">
          <v-btn text to="/login" class="mr-1">Log In</v-btn>
          <v-btn outlined to="/signup" class="mr-4">Sign Up</v-btn>
        </template>
        <template v-else>
          <v-btn text class="d-flex align-center">

            <!-- Loading Icon when Logging out -->
            <v-progress-circular v-if="isLoggingOut" indeterminate size="24"></v-progress-circular>

            <!-- Account Icon and Username -->
            <template v-else>
              <v-icon left>mdi-account</v-icon>
              {{ globalState.username }}
            </template>

            <!-- User Menu -->
            <v-menu v-if="!isLoggingOut" activator="parent" offset-y>
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
import { ref } from 'vue';
import { globalState } from '@/main.js';
import placeholderLogo from '@/assets/placeholder-logo.png';
import { useRouteClass } from '@/composables/useRouteClass';

export default {
  setup() {

    const isLoggingOut = ref(false);  // Indicates whether user is logging out

    // Method to toggle drawer state
    const toggleDrawer = () => {
      globalState.isDrawerOpen = !globalState.isDrawerOpen;
    };

    // Method to vary the color of the buttons based on the current route
    const { getButtonClass } = useRouteClass();

    // Method to handle logout
    const logout = async () => {
      isLoggingOut.value = true;
      await fetch('/api/logout');
      // Clear global state
      globalState.authenticated = false;
      globalState.username = null;
      globalState.display_name = null;
      isLoggingOut.value = false;

      // Redirect to the main page with a full page reload
      window.location.href = '/';
    };

    return {
      toggleDrawer,
      getButtonClass,
      logout,
      isLoggingOut,
      placeholderLogo,
      globalState
    };
  },
};
</script>

<style>
.first-middle-nav-button {
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
