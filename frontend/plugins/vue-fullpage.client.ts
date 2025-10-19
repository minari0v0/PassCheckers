import { defineNuxtPlugin } from '#app'
import 'fullpage.js/dist/fullpage.min.css'
import VueFullPage from 'vue-fullpage.js'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(VueFullPage)
})
