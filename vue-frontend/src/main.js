/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

import '@mdi/font/css/materialdesignicons.css';

import { createApp, reactive, watch } from 'vue';
import { createVuetify } from 'vuetify'
import App from './App.vue';
import router from './router';
import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';
import { registerPlugins } from '@/plugins';
import vuetify from './plugins/vuetify'
import './assets/app-layout.css'; // app layout


// Create a global state
export const globalState = reactive({
  authenticated: false,
  username: null,
  display_name: null,
  user_email: null, // Add user_email here
  isDrawerOpen: false, // Reactive state for the navigation drawer
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
        globalState.user_email = data.email;
                
        // Debug log to check values
        console.log('Auth Status Response:', data);
        console.log('Global State:', globalState);
    } else {
        globalState.authenticated = false;
        globalState.username = null;
        globalState.display_name = null;
        globalState.user_email = null;
    }
  });

app.use(vuetify)
app.use(router);
app.use(Toast);

app.mount('#app');