// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  ssr: false,

  modules: [
    '@vueuse/nuxt',
    '@nuxt/image',
    '@nuxt/icon',
    '@nuxt/ui',
    'nuxt-shiki',
  ],

  icon: {
    clientBundle: {
      scan: true,
      sizeLimitKb: 512,
    },
  },

  shiki: {
    bundledLangs: ['ts', 'json'],
    bundledThemes: ['github-dark-default'],
    defaultTheme: 'github-dark-default',
  },

  colorMode: {
    preference: 'dark',
  },

  css: ['~/assets/css/main.css'],

  compatibilityDate: '2025-12-14',
});
