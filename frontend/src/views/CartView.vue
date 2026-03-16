<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useCartStore } from '@/stores/cart'
import CartItem from '@/components/cart/CartItem.vue'
import CartSummary from '@/components/cart/CartSummary.vue'
import { useRouter } from 'vue-router'
import { ShoppingBag, ArrowLeft, Trash2 } from 'lucide-vue-next'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import { Button } from '@/components/ui/button'

const cartStore = useCartStore()
const { items, totalQuantity, totalAmount, isLoading } = storeToRefs(cartStore)
const router = useRouter()

const updateQuantity = (id: string, quantity: number) => {
  cartStore.updateQuantity(id, quantity)
}

const removeItem = (id: string) => {
  cartStore.removeFromCart(id)
}

const handleClearCart = async () => {
  if (confirm('確定要清空購物車嗎？')) {
    await cartStore.clearCart()
  }
}

const continueShopping = () => {
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Navbar />

    <main class="flex-grow container mx-auto py-12 px-4">
      <div class="flex items-center justify-between mb-8">
        <h1 class="text-3xl font-bold text-gray-900">購物車</h1>
        <div class="flex gap-2">
          <Button 
            v-if="items.length > 0"
            variant="outline" 
            @click="handleClearCart" 
            :disabled="isLoading"
            class="text-destructive hover:bg-destructive hover:text-destructive-foreground"
          >
            <Trash2 class="mr-2 h-4 w-4" /> 清空購物車
          </Button>
          <Button variant="ghost" @click="continueShopping" class="text-muted-foreground hover:text-primary">
            <ArrowLeft class="mr-2 h-4 w-4" /> 繼續購物
          </Button>
        </div>
      </div>

      <div v-if="items.length === 0" class="text-center py-20 bg-white rounded-xl border border-gray-100 shadow-sm">
        <div class="inline-flex bg-gray-100 p-6 rounded-full mb-6">
          <ShoppingBag class="w-12 h-12 text-gray-400" />
        </div>
        <h2 class="text-xl font-bold text-gray-900 mb-2">購物車目前是空的</h2>
        <p class="text-gray-500 mb-8">看起來您還沒有加入任何商品</p>
        <Button @click="continueShopping" class="bg-primary text-primary-foreground hover:bg-primary/90">
          去購物
        </Button>
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
    </main>

    <Footer />
  </div>
</template>