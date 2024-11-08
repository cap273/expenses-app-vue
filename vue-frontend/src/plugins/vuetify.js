// src/plugins/vuetify.js

import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { useStorage } from '@vueuse/core'
const storedTheme = useStorage('theme-preference', 'light')

// Theme configuration
const lightTheme = {
  dark: false,
  colors: {
    // Core interface colors
    background: '#E0E0E0',      // Light grey background
    surface: '#FFFFFF',         // White surface
    'surface-variant': '#f5f5f5',
    'on-surface': '#000000',
    'on-surface-variant': '#424242',
    
    // Action colors
    primary: '#1976D2',
    secondary: '#424242',
    accent: '#82B1FF',
    error: '#FF5252',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FB8C00',
    
    // Custom colors for specific components
    'chart-primary': '#1976D2',
    'chart-secondary': '#424242',
    'chart-tertiary': '#82B1FF',
    
    // Table colors
    'table-header': '#F5F5F5',
    'table-border': '#E0E0E0',
    'table-hover': '#F5F5F5',
    
    // Text colors
    'text-primary': '#000000',
    'text-secondary': '#757575',
  }
}

const darkTheme = {
  dark: true,
  colors: {
    // Core interface colors
    background: '#121212',
    surface: '#1E1E1E',
    'surface-variant': '#2A2A2A',
    'on-surface': '#FFFFFF',
    'on-surface-variant': '#EEEEEE',
    
    // Action colors
    primary: '#64B5F6',
    secondary: '#757575',
    accent: '#82B1FF',
    error: '#FF5252',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FFB74D',
    
    // Custom colors for specific components
    'chart-primary': '#64B5F6',
    'chart-secondary': '#90CAF9',
    'chart-tertiary': '#42A5F5',
    
    // Table colors
    'table-header': '#2A2A2A',
    'table-border': '#424242',
    'table-hover': '#2A2A2A',
    
    // Text colors
    'text-primary': '#FFFFFF',
    'text-secondary': '#BDBDBD',
  }
}

// Create and export Vuetify instance
export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: storedTheme.value,
    themes: {
      light: lightTheme,
      dark: darkTheme,
    },
  },
})

// Export theme configuration for use in other parts of the app
export const themeConfig = {
  light: lightTheme,
  dark: darkTheme
}