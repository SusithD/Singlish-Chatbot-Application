// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss'],

  // Aggressive fix for macOS spawn EBADF errors
  vite: {
    server: {
      fs: {
        strict: false,
        allow: ['..']
      },
      watch: {
        usePolling: true,
        interval: 1000,
        ignored: ['**/node_modules/**', '**/.git/**']
      }
    },
    optimizeDeps: {
      exclude: ['vue', '@vue/runtime-core', '@vue/runtime-dom'],
      force: true
    },
    define: {
      __VUE_PROD_DEVTOOLS__: false,
      __VUE_OPTIONS_API__: true
    }
  },

  // Development server configuration
  devServer: {
    port: 3000,
    host: 'localhost'
  },

  // Build configuration
  build: {
    transpile: []
  },

  // SSR configuration
  ssr: false,

  // Nitro configuration with more aggressive settings
  nitro: {
    experimental: {
      wasm: false
    },
    dev: true,
    minify: false
  }
})
