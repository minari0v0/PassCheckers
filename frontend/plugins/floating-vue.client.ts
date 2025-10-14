import { defineNuxtPlugin } from '#app'
import FloatingVue from 'floating-vue'
import 'floating-vue/dist/style.css'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(FloatingVue, {
    themes: {
      'passcheckers-tooltip': {
        $extend: 'tooltip',
        $vars: {
          background: '#2c3e50',
          color: 'white',
          borderRadius: '8px',
        },
      },
    },
  });
});
