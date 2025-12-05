<script setup lang="ts">
import { RouterView, RouterLink } from 'vue-router'
import { ShoppingCart } from 'lucide-vue-next'
import { useCartStore } from '@/stores/cart'

const cartStore = useCartStore()
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="container mx-auto px-4 py-4 flex items-center justify-between">
        <RouterLink to="/" class="text-2xl font-bold text-gray-900 tracking-tight hover:text-gray-700 transition-colors">
          CY E-Commerce
        </RouterLink>
        <nav class="flex items-center gap-4">
          <RouterLink to="/cart" class="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors" aria-label="Cart">
            <ShoppingCart class="w-6 h-6" />
            <span v-if="cartStore.totalQuantity > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center shadow-sm">
              {{ cartStore.totalQuantity > 99 ? '99+' : cartStore.totalQuantity }}
            </span>
          </RouterLink>
        </nav>
      </div>
    </header>

    <main class="flex-grow container mx-auto px-4 py-8">
      <RouterView />
    </main>

    <footer class="bg-gray-900 text-white py-8">
      <div class="container mx-auto px-4 text-center text-sm text-gray-400">
        &copy; 2025 CY E-Commerce. All rights reserved.
      </div>
    </footer>
  </div>
</template>