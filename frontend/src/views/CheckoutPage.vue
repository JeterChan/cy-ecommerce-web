<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCheckoutStore } from '@/stores/useCheckoutStore'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import OrderSummary from '@/components/Checkout/OrderSummary.vue'
import PurchaserForm from '@/components/Checkout/PurchaserForm.vue'
import ShippingForm from '@/components/Checkout/ShippingForm.vue'
import PaymentMethod from '@/components/Checkout/PaymentMethod.vue'
import { useCheckoutValidation } from '@/composables/useCheckoutValidation'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-vue-next'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const store = useCheckoutStore()
const cartStore = useCartStore()
const authStore = useAuthStore()
const { showError } = useToast()
const { purchaser, shipping, payment, orderNote, isSubmitting, error } = storeToRefs(store)
const { errors, validatePurchaser, validateShipping, clearErrors } = useCheckoutValidation()

// 從購物車載入商品到結帳頁面
onMounted(async () => {
  console.log('📄 [CheckoutPage] 頁面載入')

  // 1. 檢查登入狀態
  if (!authStore.isAuthenticated) {
    console.error('❌ [CheckoutPage] 使用者未登入')
    showError('請先登入後再進行結帳')
    router.push('/login?redirect=/checkout')
    return
  }

  console.log('✅ [CheckoutPage] 使用者已登入:', authStore.user?.email)

  // 2. 檢查 localStorage 中的購物車
  const storedCart = localStorage.getItem('cart')
  console.log('🔍 [CheckoutPage] localStorage 購物車:', storedCart)

  // 3. 檢查購物車 store
  console.log('🛒 [CheckoutPage] 購物車商品數量:', cartStore.items.length)
  console.log('🛒 [CheckoutPage] 購物車商品明細:', JSON.stringify(cartStore.items, null, 2))

  if (cartStore.items.length === 0) {
    console.warn('⚠️ [CheckoutPage] 購物車為空，導向回首頁')
    showError('購物車是空的，請先加入商品')
    router.push('/')
    return
  }

  // 4. 將購物車商品轉換為結帳商品格式
  const checkoutItems = cartStore.items.map(item => ({
    id: item.productId,
    name: item.name,
    price: item.price,
    quantity: item.quantity
  }))

  console.log('✅ [CheckoutPage] 準備載入商品到結帳:', checkoutItems.length, '個商品')
  console.log('📦 [CheckoutPage] 結帳商品明細:', JSON.stringify(checkoutItems, null, 2))

  // 5. 設置到 checkout store
  store.setItems(checkoutItems)

  // 6. 驗證是否成功設置
  console.log('✔️ [CheckoutPage] Checkout store 商品數量:', store.items.length)

  if (store.items.length === 0) {
    console.error('❌ [CheckoutPage] 商品未成功載入到 checkout store!')
    showError('系統錯誤：無法載入購物車商品，請重新整理頁面')
  } else {
    console.log('✅ [CheckoutPage] 商品已成功載入到結帳頁面')
  }
})

const handleSubmit = async () => {
  console.log('🔘 [CheckoutPage] 使用者點擊送出訂單')

  clearErrors()
  const isPurchaserValid = validatePurchaser(purchaser.value)
  const isShippingValid = validateShipping(shipping.value)
  
  if (!isPurchaserValid || !isShippingValid) {
    console.warn('⚠️ [CheckoutPage] 表單驗證失敗')
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }

  console.log('✅ [CheckoutPage] 表單驗證通過，開始送出訂單')

  try {
    const order = await store.submitOrder()
    console.log('🎉 [CheckoutPage] 訂單送出成功，導向成功頁面')
    router.push({ path: '/order-success', query: { orderId: order.id } })
  } catch (e) {
    console.error('❌ [CheckoutPage] 訂單送出失敗:', e)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}
const goBackToCart = () => {
  router.push('/cart')
}
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Navbar />

    <main class="flex-grow container mx-auto px-4 py-8">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold">結帳</h1>
        <Button variant="ghost" @click="goBackToCart" class="text-muted-foreground hover:text-primary">
          <ArrowLeft class="mr-2 h-4 w-4" /> 返回購物車
        </Button>
      </div>
      
      <!-- Error Alert -->
      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6 relative" role="alert">
        <span class="block sm:inline">{{ error }}</span>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Steps will go here -->
        <div class="space-y-6">
          <!-- Forms -->
          <PurchaserForm 
            v-model="purchaser" 
            :errors="errors"
          />
          
          <ShippingForm 
            v-model="shipping" 
            v-model:note="orderNote"
            :errors="errors"
          />

          <PaymentMethod 
            v-model="payment"
          />
        </div>
        <div>
          <OrderSummary />
          <Button 
            @click="handleSubmit"
            :disabled="isSubmitting"
            class="w-full h-14 text-lg font-bold mt-6"
          >
            <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isSubmitting ? '處理中...' : '送出訂單' }}
          </Button>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>
