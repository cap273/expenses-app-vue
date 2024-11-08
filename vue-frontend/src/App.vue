<template>
  <v-app>
    <v-theme-provider :theme="theme">
      <NavBar />
      <NavDrawer/>
      <v-main>
        <router-view></router-view>
      </v-main>
    </v-theme-provider>
  </v-app>
</template>

<script>
import NavBar from './components/NavBar.vue';
import NavDrawer from './components/NavDrawer.vue';

export default {
  components: { NavBar, NavDrawer },
};
</script>