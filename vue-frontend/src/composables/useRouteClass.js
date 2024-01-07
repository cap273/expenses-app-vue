// src/composables/useRouteClass.js
import { computed } from 'vue';
import { useRoute } from 'vue-router'; 

// Define a composable function to vary the color of the buttons based on the current route
export function useRouteClass() {
  const route = useRoute();

  const getButtonClass = (routeName) => {
    return computed(() => {
      return {
        'nav-button': true,
        'light-blue': route.name !== routeName,
        'dark-blue': route.name === routeName
      };
    });
  };

  return { getButtonClass };
}