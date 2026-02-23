import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/product/:id',
      name: 'product-detail',
      component: () => import('@/views/ProductDetailView.vue')
    },
    {
      path: '/cart',
      name: 'cart',
      component: () => import('@/views/CartView.vue')
    },
    {
      path: '/checkout',
      name: 'checkout',
      component: () => import('@/views/CheckoutPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/order-success',
      name: 'order-success',
      component: () => import('@/views/OrderSuccessPage.vue')
    },
    {
      path: '/orders',
      name: 'order-list',
      component: () => import('@/views/OrderListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/orders/:id',
      name: 'order-detail',
      component: () => import('@/views/OrderDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue')
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: () => import('@/views/ForgotPasswordView.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 導航守衛：保護需要認證的路由
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // 等待 auth store 初始化完成
  await authStore.waitForInit()

  // 如果有 token 但沒有 user（初始化時獲取失敗），再試一次
  if (authStore.accessToken && !authStore.user) {
    console.log('[Router] 有 token 但缺少 user，嘗試重新獲取...')
    try {
      await authStore.getCurrentUser()
      console.log('[Router] User 資訊獲取成功')
    } catch (error) {
      console.warn('[Router] User 資訊獲取失敗，但保留認證狀態')
      // 不清除狀態，允許繼續（API 攔截器會處理 token refresh）
    }
  }

  // 檢查路由是否需要認證
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 未登入，重定向到登入頁，並保存原目標路徑
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else {
    next()
  }
})

export default router