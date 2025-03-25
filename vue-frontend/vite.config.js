import vue from '@vitejs/plugin-vue'
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
import ViteFonts from 'unplugin-fonts/vite'
import { defineConfig, loadEnv } from 'vite'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())

  // Janusz code for remote server access
  const isRemote = process.env.REMOTE === '1' || env.VITE_REMOTE === '1';
  console.log("VITE SERVER HOST:", env.REMOTE);  // Debugging output


  return {
    plugins: [
      vue({ template: { transformAssetUrls } }),
      vuetify({ autoImport: true }),
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
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
      extensions: ['.js', '.json', '.jsx', '.mjs', '.ts', '.tsx', '.vue'],
    },
    server: {
      host: isRemote ? '0.0.0.0' :  '127.0.0.1', // Explicitly use IPv4 for local development
      port: 3000, // The port of the Vue app
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:5000', // Flask server on port 5000 using IPv4
          changeOrigin: true,
        },
      },
      //janusz host
      allowedHosts: ['localhost3000.thatgoodshit.com'],
      sourcemap: true, // Enable for debugging
    },
    build: {
      sourcemap: true, // Enable for debugging
    },
  }
})