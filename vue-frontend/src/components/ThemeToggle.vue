// src/components/ThemeToggle.vue
<template>
  <v-btn
    icon
    @click="toggleTheme"
    :title="theme.global.current.value.dark ? 'Switch to light mode' : 'Switch to dark mode'"
  >
    <v-icon>
      {{ theme.global.current.value.dark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}
    </v-icon>
  </v-btn>
</template>

<script>
import { useTheme } from 'vuetify'
import { useStorage } from '@vueuse/core'

export default {
  name: 'ThemeToggle',
  setup() {
    const theme = useTheme()
    const storedTheme = useStorage('theme-preference', 'light')

    const toggleTheme = () => {
      const newTheme = theme.global.current.value.dark ? 'light' : 'dark'
      theme.global.name.value = newTheme
      storedTheme.value = newTheme // Save the new preference
    }

    return {
      theme,
      toggleTheme
    }
  }
}
</script>
