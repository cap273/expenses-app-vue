// src/plugins/theme.js

import { ref } from 'vue'

// Define theme colors for light and dark modes
export const themeConfig = {
  light: {
    dark: false,
    colors: {
      primary: '#1976D2',
      secondary: '#424242',
      accent: '#82B1FF',
      error: '#FF5252',
      info: '#2196F3',
      success: '#4CAF50',
      warning: '#FB8C00',
      background: '#E0E0E0',
      surface: '#FFFFFF',
      'on-surface': '#000000',
      'surface-variant': '#f5f5f5',
      'on-surface-variant': '#424242',
      // Chart colors
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
  },
  dark: {
    dark: true,
    colors: {
      primary: '#64B5F6',
      secondary: '#757575',
      accent: '#82B1FF',
      error: '#FF5252',
      info: '#2196F3',
      success: '#4CAF50',
      warning: '#FB8C00',
      background: '#121212',
      surface: '#1E1E1E',
      'on-surface': '#FFFFFF',
      'surface-variant': '#2A2A2A',
      'on-surface-variant': '#EEEEEE',
      // Chart colors
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
}

// Theme composable
export function useTheme() {
  const isDark = ref(false)

  // Toggle theme function
  const toggleTheme = () => {
    isDark.value = !isDark.value
    document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  }

  // Initialize theme
  const initTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      isDark.value = savedTheme === 'dark'
      document.documentElement.setAttribute('data-theme', savedTheme)
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      isDark.value = prefersDark
      document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
    }
  }

  return {
    isDark,
    toggleTheme,
    initTheme
  }
}

// Chart theme settings
export const getChartTheme = (isDark) => ({
  plugins: {
    legend: {
      labels: {
        color: isDark ? '#FFFFFF' : '#000000'
      }
    }
  },
  scales: {
    x: {
      grid: {
        color: isDark ? '#424242' : '#E0E0E0'
      },
      ticks: {
        color: isDark ? '#FFFFFF' : '#000000'
      }
    },
    y: {
      grid: {
        color: isDark ? '#424242' : '#E0E0E0'
      },
      ticks: {
        color: isDark ? '#FFFFFF' : '#000000'
      }
    }
  }
})