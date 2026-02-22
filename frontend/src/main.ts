import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import { i18n } from './i18n'
import { useAuthStore } from './stores/auth'
import { useCartStore } from './stores/cart'
import { setTokenExpiredCallback } from './lib/api'
import { useToast } from './composables/useToast'
import { setupZodErrorMap } from './lib/zodErrorMap'

const app = createApp(App)
const pinia = createPinia()

// 設定 Zod 錯誤訊息為正體中文
setupZodErrorMap()

app.use(pinia)
app.use(router)
app.use(i18n)

// 設定 Token 過期回調
setTokenExpiredCallback(() => {
  const authStore = useAuthStore()
  const { showError } = useToast()

  authStore.logout()
  showError('登入已過期，請重新登入')
  router.push('/login')
})

// 初始化 Auth Store 和 Cart Store
const authStore = useAuthStore()
const cartStore = useCartStore()

authStore.initAuth().then(() => {
  // 認證完成後，同步購物車
  cartStore.syncFromBackend().catch(err => {
    console.warn('購物車同步失敗，使用本地資料:', err)
  })
}).finally(() => {
  app.mount('#app')
})


