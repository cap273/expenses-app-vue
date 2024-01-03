<template>
  <v-app-bar app>
    <v-toolbar-title>
      <v-img :src="placeholderLogo" @click="$router.push('/')" class="clickable"></v-img>
    </v-toolbar-title>

    <v-spacer></v-spacer>

    <v-btn text href="#features">Features</v-btn>
    <v-btn text href="#pricing">Pricing</v-btn>
    <v-btn text href="#faq">FAQ</v-btn>

    <v-spacer></v-spacer>

    <template v-if="!globalState.authenticated">
      <v-btn text to="/login">Log In</v-btn>
      <v-btn outlined to="/signup">Sign Up</v-btn>
    </template>

    <template v-else>
      <v-btn text>
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
        'active-route': this.$route.name === routeName
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

.active-route {
  text-decoration: underline;
  text-decoration-color: darkblue;
  color: darkblue;
}
</style>
