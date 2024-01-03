/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { registerPlugins } from '@/plugins';

import { reactive } from 'vue';

// Create a global state
export const globalState = reactive({
  authenticated: false,
  username: null,
  display_name: null
});

const app = createApp(App);
registerPlugins(app);

// Check user's authentication status
fetch('/api/auth/status')
  .then(response => response.json())
  .then(data => {
    if (data.authenticated) {
        globalState.authenticated = true;
        globalState.username = data.username;
        globalState.display_name = data.display_name;
    } else {
        globalState.authenticated = false;
        globalState.username = null;
        globalState.display_name = null;
    }
  });

app.use(router);

app.mount('#app');
