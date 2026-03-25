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
    'nuxt-umami',
  ],

  icon: {
    clientBundle: {
      scan: true,
      sizeLimitKb: 512,
    },
  },

  shiki: {
    bundledLangs: ['ts', 'json', 'python', 'rust', 'go'],
    bundledThemes: ['github-dark-default'],
    defaultTheme: 'github-dark-default',
  },

  colorMode: {
    preference: 'dark',
  },

  css: ['~/assets/css/main.css'],

  umami: {
    id: 'c6528c3b-6dde-4f9e-befb-b6bdd5e4b057',
    host: 'https://cloud.umami.is/',
  },

  compatibilityDate: '2025-12-14',
});
