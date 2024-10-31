import { useColorMode } from '@vueuse/core'
import { watch } from 'vue'

export const useAppColorMode = () => {
  const colorMode = useColorMode({
    selector: 'html',
    attribute: 'data-color-mode',
    storageKey: 'app-color-mode',
    modes: {
      light: 'light',
      dark: 'dark',
      sepia: 'sepia',
      cafe: 'cafe'
    },
    initialValue: 'light'
  })

  // Watch for changes and update Vuetify theme
  watch(colorMode, (newMode) => {
    // Update CSS variables based on mode
    document.documentElement.setAttribute('data-color-mode', newMode)
  }, { immediate: true })

  return colorMode
}