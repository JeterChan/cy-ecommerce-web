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
      redirect: '/auth/forgot-password'
    },
    {
      path: '/reset-password',
      redirect: '/auth/reset-password'
    },
    {
      path: '/email-verify',
      redirect: '/email/verify'
    },
    {
      path: '/auth/forgot-password',
      name: 'forgot-password',
      component: () => import('@/views/auth/ForgotPasswordView.vue')
    },
    {
      path: '/auth/reset-password',
      name: 'reset-password',
      component: () => import('@/views/auth/ResetPasswordView.vue')
    },
    {
      path: '/email/verify',
      name: 'email-verify',
      component: () => import('@/views/auth/VerifyEmailView.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/AdminDashboard.vue'),
          meta: { title: '儀表板' }
        },
        {
          path: 'products',
          name: 'admin-products',
          component: () => import('@/views/admin/ProductManagementView.vue'),
          meta: { title: '商品管理' }
        },
        {
          path: 'categories',
          name: 'admin-categories',
          component: () => import('@/views/admin/CategoryManagementView.vue'),
          meta: { title: '分類管理' }
        },
        {
          path: 'orders',
          name: 'admin-orders',
          component: () => import('@/views/admin/OrderManagementView.vue'),
          meta: { title: '訂單管理' }
        }
      ]
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
      // 無法驗證使用者身分（網路錯誤或 token 失效），清除認證狀態強制重新登入
      // 不能「允許繼續」：若 user 為 null，requiresAdmin 檢查會立即失敗並導向 /
      console.warn('[Router] User 資訊獲取失敗，清除認證狀態')
      authStore.logout()
    }
  }

  // 檢查路由是否需要認證
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 未登入，重定向到登入頁，並保存原目標路徑
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (to.meta.requiresAdmin) {
    if (!authStore.user) {
      // 有 token 但 user 仍為 null（不應發生，防禦性處理）
      next({ path: '/login', query: { redirect: to.fullPath } })
    } else if (authStore.user.role !== 'admin') {
      // 已登入但非管理員角色
      console.warn('[Router] 嘗試存取管理員頁面，但權限不足')
      next({ path: '/' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router