<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useCartStore } from '@/stores/cart'
import CartItem from '@/components/cart/CartItem.vue'
import CartSummary from '@/components/cart/CartSummary.vue'
import { RouterLink } from 'vue-router'
import { ShoppingBag } from 'lucide-vue-next'

const cartStore = useCartStore()
const { items, totalQuantity, totalAmount } = storeToRefs(cartStore)

const updateQuantity = (id: string, quantity: number) => {
  cartStore.updateQuantity(id, quantity)
}

const removeItem = (id: string) => {
  cartStore.removeFromCart(id)
}
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-8 text-gray-900">購物車</h1>

    <div v-if="items.length === 0" class="text-center py-20 bg-white rounded-xl border border-gray-100 shadow-sm">
      <div class="inline-flex bg-gray-100 p-6 rounded-full mb-6">
        <ShoppingBag class="w-12 h-12 text-gray-400" />
      </div>
      <h2 class="text-xl font-bold text-gray-900 mb-2">購物車目前是空的</h2>
      <p class="text-gray-500 mb-8">看起來您還沒有加入任何商品</p>
      <RouterLink to="/" class="inline-block bg-slate-900 text-white py-3 px-8 rounded-lg font-bold hover:bg-slate-800 transition-transform active:scale-[0.98]">
        去購物
      </RouterLink>
    </div>

    <div v-else class="lg:flex lg:gap-12">
      <!-- Cart Items List -->
      <div class="flex-1">
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6 mb-8 lg:mb-0">
          <div class="hidden sm:flex text-sm text-gray-500 pb-4 border-b border-gray-100 font-medium">
            <div class="flex-1">商品資訊</div>
            <div class="w-40 text-center">數量</div>
            <div class="w-24 text-right">小計</div>
            <div class="w-12"></div>
          </div>
          
          <div class="divide-y divide-gray-100">
            <CartItem 
              v-for="item in items" 
              :key="item.productId" 
              :item="item"
              @update-quantity="updateQuantity"
              @remove="removeItem"
            />
          </div>
        </div>
      </div>

      <!-- Summary -->
      <div class="lg:w-80 flex-shrink-0">
        <CartSummary 
          :total-quantity="totalQuantity" 
          :total-amount="totalAmount" 
        />
      </div>
    </div>
  </div>
</template>