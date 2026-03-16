<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { 
  LayoutDashboard, 
  Package, 
  LogOut, 
  ExternalLink,
  Menu,
  X,
  Tag
} from 'lucide-vue-next'
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const authStore = useAuthStore()
const router = useRouter()
const { showSuccess } = useToast()

const isSidebarOpen = ref(false)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const handleLogout = async () => {
  await authStore.logout()
  showSuccess('已成功登出')
  router.push('/')
}

const navItems = [
  { name: '儀表板', path: '/admin/dashboard', icon: LayoutDashboard },
  { name: '商品管理', path: '/admin/products', icon: Package },
  { name: '分類管理', path: '/admin/categories', icon: Tag },
]
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex">
    <!-- Sidebar -->
    <aside 
      :class="[
        'bg-slate-900 text-white w-64 fixed inset-y-0 left-0 z-50 transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0',
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <div class="p-6 flex items-center justify-between">
        <div class="flex items-center gap-2 font-bold text-xl tracking-wider">
          <span class="text-primary">CY</span>
          <span>ADMIN</span>
        </div>
        <button @click="toggleSidebar" class="lg:hidden">
          <X class="w-6 h-6" />
        </button>
      </div>

      <nav class="mt-6 px-4 space-y-2">
        <RouterLink 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors"
          active-class="bg-primary text-primary-foreground"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span>{{ item.name }}</span>
        </RouterLink>
      </nav>

      <div class="absolute bottom-0 w-full p-4 space-y-2 border-t border-slate-800">
        <RouterLink 
          to="/"
          class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors text-slate-400 hover:text-white"
        >
          <ExternalLink class="w-5 h-5" />
          <span>查看前台</span>
        </RouterLink>
        <button 
          @click="handleLogout"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-red-900/50 transition-colors text-red-400 hover:text-red-300"
        >
          <LogOut class="w-5 h-5" />
          <span>登出</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <!-- Header -->
      <header class="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-4 lg:px-8 shrink-0">
        <div class="flex items-center gap-4">
          <button @click="toggleSidebar" class="p-2 hover:bg-gray-100 rounded-md lg:hidden">
            <Menu class="w-6 h-6" />
          </button>
          <h2 class="text-lg font-semibold text-gray-800">
            {{ $route.meta.title || '' }}
          </h2>
        </div>

        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-500 hidden sm:inline">
            {{ authStore.user?.username }} (管理員)
          </span>
          <div class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-bold uppercase">
            {{ authStore.user?.username?.charAt(0) }}
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-y-auto p-4 lg:p-8">
        <RouterView />
      </main>
    </div>

    <!-- Mobile Overlay -->
    <div 
      v-if="isSidebarOpen" 
      @click="toggleSidebar"
      class="fixed inset-0 bg-black/50 z-40 lg:hidden"
    ></div>
  </div>
</template>

<style scoped>
.router-link-exact-active {
  @apply bg-primary text-primary-foreground;
}
</style>
