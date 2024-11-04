// Plugins
import vue from '@vitejs/plugin-vue'
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
import ViteFonts from 'unplugin-fonts/vite'

// Utilities
import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue({
      template: { transformAssetUrls }
    }),
    // https://github.com/vuetifyjs/vuetify-loader/tree/master/packages/vite-plugin#readme
    vuetify({
      autoImport: true,
    }),
    ViteFonts({
      google: {
        families: [{
          name: 'Roboto',
          styles: 'wght@100;300;400;500;700;900',
        }],
      },
    }),
  ],
  define: { 'process.env': {} },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
    extensions: [
      '.js',
      '.json',
      '.jsx',
      '.mjs',
      '.ts',
      '.tsx',
      '.vue',
    ],
  },
  server: {
    port: 3000, // Your desired port for the Vue app
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // The URL of your Flask server
        changeOrigin: true,
      }
    },
    sourcemap: false, // Add this to disable source maps in the dev server
  },
  // Configuration options for the build process
  build: {
    // `sourcemap: false` disables source map generation
    // Source maps help with debugging by mapping compiled code back to original source code,
    // but they can cause errors if the source maps for certain libraries are missing.
    // Disabling source maps prevents these errors in the browser console and is usually
    // recommended in production to reduce build size and avoid unnecessary warnings.
    sourcemap: false,
  },
})
