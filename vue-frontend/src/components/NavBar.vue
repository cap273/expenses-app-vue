<template>

    <!-- Navigation Drawer -->
    <v-navigation-drawer
      v-model="drawer"
      temporary
    >
      <v-list>
        <template v-if="!globalState.authenticated">
          <v-list-item link href="#features">
            <v-list-item-title>Features</v-list-item-title>
          </v-list-item>
          <v-list-item link href="#pricing">
            <v-list-item-title>Pricing</v-list-item-title>
          </v-list-item>
          <!--
                    <v-list-item link to="/login">
            <v-list-item-title>Log In</v-list-item-title>
          </v-list-item>
          <v-list-item link to="/signup">
            <v-list-item-title>Sign Up</v-list-item-title>
          </v-list-item>
           -->
        </template>
          <template v-else>
          <v-list-item link to="/view_expenses">
            <v-list-item-title>View Expenses</v-list-item-title>
          </v-list-item>
          <v-list-item @click="logout">
            <v-list-item-title>Log Out</v-list-item-title>
          </v-list-item>
        </template>
      </v-list>
    </v-navigation-drawer>

  <v-app-bar app>
    <!-- Wrap navbar content in a container with max-width of 1400px -->
    <v-container fluid class="container-1400">
      <v-row no-gutters class="align-center">
        <!-- Left Column: Logo -->
        <v-col cols="auto" class="d-flex align-center">
          <!-- Hamburger Menu Icon (Visible only on small screens) -->
          <v-btn icon class="d-lg-none mr-2" @click="drawer = !drawer">
          <v-icon>mdi-menu</v-icon>
        </v-btn>
          <v-img
            src="@/assets/randomSimpleLogo.png"
            width="50"
            height="50"
            alt="Logo"
            @click="$router.push('/')"
            class="clickable"
          ></v-img>
        </v-col>

        <!-- Middle Column: Navigation Links -->
        <v-col cols="auto" class="d-none d-lg-flex align-center">
        <!--Regular size for normal-->
          <template v-if="!globalState.authenticated">
            <v-btn text href="#features" class="first-nav-button">Features</v-btn>
            <v-btn text href="#pricing">Pricing</v-btn>
          </template>
          <template v-else>
            <!-- 
              <v-btn
              text
              :class="[getButtonClass('InputExpenses'), 'first-middle-nav-button']"
              to="/input_expenses"
            >Input Expenses</v-btn>
            -->
            <v-btn
              text
              :class="getButtonClass('ViewExpenses')"
              to="/view_expenses"
            >View Expenses</v-btn>
          </template>
        </v-col>

        <!-- Right Column: User Actions -->
        <v-spacer></v-spacer>

        <v-col cols="auto" class="d-flex align-center">
          <template v-if="!globalState.authenticated">
            <v-btn text to="/login" class="mr-1">Log In</v-btn>
            <v-btn outlined to="/signup" class="mr-4">Sign Up</v-btn>
          </template>
          <template v-else>
            <v-btn text class="d-flex align-center">
              <!-- Loading Icon when Logging out -->
              <v-progress-circular
                v-if="isLoggingOut"
                indeterminate
                size="24"
              ></v-progress-circular>

              <!-- Account Icon and Username -->
              <template v-else>
                <v-icon left>mdi-account</v-icon>
                {{ globalState.username }}
              </template>

              <!-- User Menu -->
              <v-menu v-if="!isLoggingOut" activator="parent" offset-y>
                <v-list>
                  <v-list-item link :to="{ name: 'Profile' }">
                    <v-list-item-title>
                      <v-icon left>mdi-account-circle</v-icon>
                      Profile</v-list-item-title>
                  </v-list-item>
                  <v-list-item link :to="{ name: 'HouseholdSettings' }">
                    <v-list-item-title>
                      <v-icon left>mdi-home-account</v-icon>
                      Household Settings
                    </v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="logout">
                    <v-list-item-title>
                      <v-icon left>mdi-logout</v-icon>
                      Log Out</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </v-btn>
          </template>
        </v-col>
      </v-row>
    </v-container>
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
    const drawer = ref(false); // Controls the navigation drawer


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
      drawer,
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

.container-1400 {
  max-width: 1400px !important;
  margin: 0 auto;
}

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

/* Adjust the margin or padding as needed */
.mr-1 {
  margin-right: 8px;
}

.mr-4 {
  margin-right: 32px;
}

.d-none {
  display: none !important;
}

.d-lg-flex {
  display: flex !important;
}

.d-lg-none {
  display: none !important;
}

@media (min-width: 1280px) {
  .d-lg-none {
    display: none !important;
  }
  .d-lg-flex {
    display: flex !important;
  }
}

@media (max-width: 1280px) {
  .d-lg-none {
    display: block !important;
  }
  .d-lg-flex {
    display: none !important;
  }
}

</style>