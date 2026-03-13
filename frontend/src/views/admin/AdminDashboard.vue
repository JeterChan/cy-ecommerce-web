<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Package, 
  AlertTriangle, 
  ArrowRight,
  ShoppingCart,
  TrendingUp,
  ExternalLink
} from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

const authStore = useAuthStore()

// Mock 統計數據
const stats = [
  { 
    title: '商品總數', 
    value: '128', 
    icon: Package, 
    color: 'text-blue-600',
    bg: 'bg-blue-100'
  },
  { 
    title: '低庫存警示', 
    value: '5', 
    icon: AlertTriangle, 
    color: 'text-amber-600',
    bg: 'bg-amber-100'
  },
  { 
    title: '今日訂單', 
    value: '12', 
    icon: ShoppingCart, 
    color: 'text-emerald-600',
    bg: 'bg-emerald-100'
  },
  { 
    title: '銷售額', 
    value: 'NT$ 42,500', 
    icon: TrendingUp, 
    color: 'text-indigo-600',
    bg: 'bg-indigo-100'
  },
]
</script>

<template>
  <div class="space-y-8">
    <!-- Welcome Section -->
    <div class="flex flex-col gap-2">
      <h1 class="text-3xl font-bold tracking-tight text-gray-900">
        歡迎回來，{{ authStore.user?.username }} 👋
      </h1>
      <p class="text-gray-500">
        這是您的管理後台概覽。在這裡您可以管理商品、查看訂單與掌握商店狀況。
      </p>
    </div>

    <!-- Stats Grid -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card v-for="stat in stats" :key="stat.title" class="border-none shadow-sm">
        <CardHeader class="flex flex-row items-center justify-between pb-2 space-y-0">
          <CardTitle class="text-sm font-medium text-gray-500">
            {{ stat.title }}
          </CardTitle>
          <div :class="['p-2 rounded-md', stat.bg]">
            <component :is="stat.icon" :class="['w-4 h-4', stat.color]" />
          </div>
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ stat.value }}</div>
        </CardContent>
      </Card>
    </div>

    <!-- Quick Actions -->
    <div class="grid gap-6 md:grid-cols-2">
      <Card class="border-none shadow-sm overflow-hidden">
        <CardHeader class="bg-white border-b border-gray-50">
          <CardTitle>快速操作</CardTitle>
        </CardHeader>
        <CardContent class="p-0">
          <div class="divide-y divide-gray-100">
            <RouterLink 
              to="/admin/products" 
              class="flex items-center justify-between p-4 hover:bg-gray-50 transition-colors group"
            >
              <div class="flex items-center gap-3">
                <div class="p-2 bg-slate-100 rounded-full group-hover:bg-primary/10 transition-colors">
                  <Package class="w-5 h-5 text-slate-600 group-hover:text-primary" />
                </div>
                <div>
                  <div class="font-medium text-gray-900">管理商品目錄</div>
                  <div class="text-xs text-gray-500">新增、編輯或下架您的商品</div>
                </div>
              </div>
              <ArrowRight class="w-4 h-4 text-gray-300 group-hover:text-primary transition-colors" />
            </RouterLink>

            <RouterLink 
              to="/" 
              class="flex items-center justify-between p-4 hover:bg-gray-50 transition-colors group"
            >
              <div class="flex items-center gap-3">
                <div class="p-2 bg-slate-100 rounded-full group-hover:bg-primary/10 transition-colors">
                  <ExternalLink class="w-5 h-5 text-slate-600 group-hover:text-primary" />
                </div>
                <div>
                  <div class="font-medium text-gray-900">查看前台商城</div>
                  <div class="text-xs text-gray-500">從客戶視角檢視您的網站</div>
                </div>
              </div>
              <ArrowRight class="w-4 h-4 text-gray-300 group-hover:text-primary transition-colors" />
            </RouterLink>
          </div>
        </CardContent>
      </Card>

      <Card class="border-none shadow-sm flex flex-col items-center justify-center p-8 text-center bg-slate-900 text-white">
        <div class="p-4 bg-slate-800 rounded-full mb-4">
          <TrendingUp class="w-12 h-12 text-primary" />
        </div>
        <h3 class="text-xl font-bold mb-2">準備好提升銷量了嗎？</h3>
        <p class="text-slate-400 text-sm mb-6">
          定期更新商品內容並確保庫存充足是成功的關鍵。
        </p>
        <RouterLink 
          to="/admin/products"
          class="inline-flex items-center justify-center rounded-md bg-primary px-6 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20"
        >
          立即管理商品
        </RouterLink>
      </Card>
    </div>
  </div>
</template>
