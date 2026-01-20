import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import { i18n } from './i18n'
import { useAuthStore } from './stores/auth'
import { setTokenExpiredCallback } from './lib/api'
import { useToast } from './composables/useToast'

const app = createApp(App)
const pinia = createPinia()

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

// 初始化 Auth Store（從 storage 恢復狀態）
const authStore = useAuthStore()
authStore.initAuth().finally(() => {
  app.mount('#app')
})
