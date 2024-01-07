<template>
    <v-navigation-drawer v-model="drawerOpen" temporary>
        <template v-if="!globalState.authenticated">
            <v-btn text href="#features" class="first-nav-button">Features</v-btn>
            <v-btn text href="#pricing">Pricing</v-btn>
        </template>
        <template v-else>
            <v-btn text :class="[getButtonClass('InputExpenses'), 'first-nav-button']" to="/input_expenses">Input Expenses</v-btn>
            <v-btn text :class="getButtonClass('ViewExpenses')" to="/view_expenses">View Expenses</v-btn>
        </template>
    </v-navigation-drawer>
</template>

<script>
import { ref, watch } from 'vue';
import { globalState } from '@/main.js';
import { useRouteClass } from '@/composables/useRouteClass';

export default {
  setup() {

    // Method to vary the color of the buttons based on the current route
    const { getButtonClass } = useRouteClass();

    // Local state synced with global state
    const drawerOpen = ref(globalState.isDrawerOpen);

    // Watch for changes in global state and update local state
    watch(
      () => globalState.isDrawerOpen,
      (newVal) => {
        drawerOpen.value = newVal;
      }
    );

    // Sync back changes to global state
    watch(drawerOpen, (newVal) => {
      globalState.isDrawerOpen = newVal;
    });

    return { getButtonClass, drawerOpen, globalState };
  },
};
</script>
  