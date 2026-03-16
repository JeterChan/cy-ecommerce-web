<script setup lang="ts">
import { RouterView } from 'vue-router'
import { Toaster } from '@/components/ui/toast'
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'

const authStore = useAuthStore()
const cartStore = useCartStore()

// 應用啟動時，如果用戶已登入，從後端同步購物車
onMounted(async () => {
  console.log('🚀 [App] 應用初始化...')
  console.log('🔐 [App] 用戶登入狀態:', authStore.isAuthenticated)

  if (authStore.isAuthenticated) {
    console.log('👤 [App] 檢測到已登入用戶，開始同步購物車...')
    try {
      await cartStore.syncFromBackend()
      console.log('✅ [App] 購物車同步完成')
    } catch (error) {
      console.warn('⚠️ [App] 購物車同步失敗，使用本地資料:', error)
    }
  } else {
    console.log('👤 [App] 訪客模式，使用本地購物車')
  }
})
</script>

<template>
  <RouterView />
  <Toaster />
</template>