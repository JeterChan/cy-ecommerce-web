<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { ShoppingCart, Menu, ChevronDown } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { useCartStore } from '@/stores/cart'
import { productService } from '@/services/productService'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'

const cartStore = useCartStore()
const router = useRouter()
const categories = ref<string[]>([])
const isMobileMenuOpen = ref(false)

onMounted(async () => {
  try {
    categories.value = await productService.getTags()
  } catch (e) {
    console.error('Failed to load categories:', e)
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
