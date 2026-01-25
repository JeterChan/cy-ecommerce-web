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
    }
  ]
})

// 導航守衛：保護需要認證的路由
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

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