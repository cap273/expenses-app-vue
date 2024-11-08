<!-- src/components/ThemeToggle.vue -->
<template>
    <v-btn
      icon
      @click="theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'"
      :title="theme.global.current.value.dark ? 'Switch to light mode' : 'Switch to dark mode'"
    >
      <v-icon>
        {{ theme.global.current.value.dark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}
      </v-icon>
    </v-btn>
  </template>
  
  <script>
  import { useTheme } from 'vuetify'
  
  export default {
    name: 'ThemeToggle',
    setup() {
      const theme = useTheme()
  
      return {
        theme
      }
    }
  }
  </script>