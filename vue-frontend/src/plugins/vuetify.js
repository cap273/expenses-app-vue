/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify } from 'vuetify'

// Import Vuetify components and directives
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
// plugins/vuetify.js

export default createVuetify({
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          background: '#E0E0E0',      // Light grey background
          surface: '#FFFFFF',         // White surface
          'surface-variant': '#EEEEEE',
          'on-surface': '#000000',
          'on-surface-variant': '#000000',
          primary: '#1867C0',
          secondary: '#5CBBF6',
          error: '#B00020',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FB8C00',
        }
      },
      dark: {
        dark: true,
        colors: {
          background: '#121212',
          surface: '#1E1E1E',
          'surface-variant': '#2A2A2A',
          'on-surface': '#FFFFFF',
          'on-surface-variant': '#EEEEEE',
          primary: '#64B5F6',
          secondary: '#90CAF9',
          error: '#CF6679',
          info: '#64B5F6',
          success: '#81C784',
          warning: '#FFB74D',
        }
      }
    }
  }
})