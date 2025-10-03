// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ["nuxt-quasar-ui"],
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  css: [
    '~/assets/main.css'
  ],
  devServer: {
    port: 80,
    host: '0.0.0.0'
  },
  router: {
    options: {
      scrollBehaviorType: 'smooth'
    }
  },
  vite: {
    server: {
      hmr: {
        host: '0.0.0.0',
        port: 80
      },
      
      allowedHosts: [
        'passcheckers.kro.kr',
        'localhost',
        '127.0.0.1'
      ]
    },
    logLevel: 'error' // 경고 메시지 숨기기
  },
  vue: {
    compilerOptions: {
      isCustomElement: (tag) => false
    }
  }
})