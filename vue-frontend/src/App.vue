<template>
  <v-app>
    <NavBar :username="username" />
    <v-main> <!-- Ensures content is below the app bar -->
      <router-view @update:user="username = $event" />
    </v-main>
  </v-app>
</template>

<script>
import NavBar from './components/NavBar.vue';

export default {
  components: { NavBar },
  data() {
    return {
      username: null
    };
  }
};
</script>