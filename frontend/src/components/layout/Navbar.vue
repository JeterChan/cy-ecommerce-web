<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { ShoppingCart, Menu, ChevronDown, User } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { productService } from '@/services/productService'
import { useToast } from '@/composables/useToast'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'

const cartStore = useCartStore()
const authStore = useAuthStore()
const router = useRouter()
const { t } = useI18n()
const { showSuccess } = useToast()
const categories = ref<string[]>([])
const isMobileMenuOpen = ref(false)

onMounted(async () => {
  try {
    categories.value = await productService.getTags()
  } catch (e) {
    console.error('Failed to load categories:', e)
  }

  // 如果有 token 但沒有 user，嘗試重新獲取
  if (authStore.accessToken && !authStore.user) {
    console.log('[Navbar] 偵測到有 token 但缺少 user，嘗試獲取...')
    try {
      await authStore.getCurrentUser()
      console.log('[Navbar] User 資訊獲取成功')
    } catch (error) {
      console.warn('[Navbar] User 資訊獲取失敗:', error)
    }
  }
})

const navigateToCategory = (category: string) => {
  if (category) {
    router.push({ name: 'home', query: { tag: category } })
  } else {
    router.push({ name: 'home', query: { view: 'all' } })
  }
  isMobileMenuOpen.value = false
}

const handleLogout = () => {
  authStore.logout()
  showSuccess(t('auth.logoutSuccess'))
  router.push('/login')
}
</script>

<template>
  <header class="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
    <div class="container mx-auto flex h-16 items-center px-4">
      <!-- Mobile Menu Trigger -->
      <Sheet v-model:open="isMobileMenuOpen">
        <SheetTrigger as-child>
          <Button variant="ghost" size="icon" class="md:hidden mr-2">
            <Menu class="h-5 w-5" />
            <span class="sr-only">開啟選單</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" class="w-[240px] sm:w-[300px]">
          <nav class="flex flex-col gap-4 mt-8">
            <RouterLink to="/" class="text-lg font-semibold" @click="isMobileMenuOpen = false">
              首頁
            </RouterLink>
            <div class="space-y-2">
              <h3 class="font-medium text-muted-foreground">商品分類</h3>
              <Button 
                variant="ghost" 
                class="w-full justify-start pl-4"
                @click="navigateToCategory('')"
              >
                全部商品
              </Button>
              <Button 
                v-for="category in categories" 
                :key="category"
                variant="ghost" 
                class="w-full justify-start pl-4"
                @click="navigateToCategory(category)"
              >
                {{ category }}
              </Button>
            </div>
          </nav>
        </SheetContent>
      </Sheet>

      <!-- Logo -->
      <RouterLink to="/" class="mr-6 flex items-center space-x-2">
        <span class="hidden font-bold sm:inline-block text-xl">CY E-Commerce</span>
        <span class="font-bold sm:hidden text-xl">CY</span>
      </RouterLink>

      <!-- Desktop Navigation -->
      <nav class="hidden md:flex items-center space-x-6 text-sm font-medium">
        <RouterLink to="/" class="transition-colors hover:text-foreground/80 text-foreground/60">
          首頁
        </RouterLink>
        
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button variant="ghost" class="h-8 px-2 gap-1 hover:bg-transparent">
              商品分類 <ChevronDown class="h-4 w-4 opacity-50" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem 
              @click="navigateToCategory('')"
              class="cursor-pointer"
            >
              全部商品
            </DropdownMenuItem>
            <DropdownMenuItem 
              v-for="category in categories" 
              :key="category"
              @click="navigateToCategory(category)"
              class="cursor-pointer"
            >
              {{ category }}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </nav>

      <!-- Right Side Actions -->
      <div class="flex flex-1 items-center justify-end space-x-2">
        <!-- 未登入：顯示登入/註冊按鈕 -->
        <template v-if="!authStore.isAuthenticated">
          <Button variant="ghost" as-child class="hidden sm:flex">
            <RouterLink to="/login">{{ t('auth.login') }}</RouterLink>
          </Button>
          <Button as-child>
            <RouterLink to="/register">{{ t('auth.register') }}</RouterLink>
          </Button>
        </template>

        <!-- 已登入：顯示使用者選單 -->
        <template v-else>
          <!-- 桌面版：顯示 username -->
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="ghost" class="hidden md:flex gap-1">
                {{ authStore.user?.username }}
                <ChevronDown class="h-4 w-4 opacity-50" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem as-child class="cursor-pointer">
                <RouterLink to="/profile">{{ t('auth.profile') }}</RouterLink>
              </DropdownMenuItem>
              <DropdownMenuItem as-child class="cursor-pointer">
                <RouterLink to="/orders">{{ t('auth.orders') }}</RouterLink>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="handleLogout" class="cursor-pointer">
                {{ t('auth.logout') }}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <!-- 移動版：顯示 User icon -->
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="ghost" size="icon" class="flex md:hidden">
                <User class="h-5 w-5" />
                <span class="sr-only">使用者選單</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <div class="md:hidden px-2 py-1.5 text-sm font-semibold">
                {{ authStore.user?.username }}
              </div>
              <DropdownMenuSeparator class="md:hidden" />
              <DropdownMenuItem as-child class="cursor-pointer">
                <RouterLink to="/profile">{{ t('auth.profile') }}</RouterLink>
              </DropdownMenuItem>
              <DropdownMenuItem as-child class="cursor-pointer">
                <RouterLink to="/orders">{{ t('auth.orders') }}</RouterLink>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="handleLogout" class="cursor-pointer">
                {{ t('auth.logout') }}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </template>

        <!-- 購物車 -->
        <Button variant="ghost" size="icon" as-child class="relative">
          <RouterLink to="/cart">
            <ShoppingCart class="h-6 w-6" />
            <span class="sr-only">購物車</span>
            <span 
              v-if="cartStore.totalQuantity > 0" 
              class="absolute top-0 right-0 inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 border-2 border-background rounded-full -translate-y-1/2 translate-x-1/2"
            >
              {{ cartStore.totalQuantity }}
            </span>
          </RouterLink>
        </Button>
      </div>
    </div>
  </header>
</template>
