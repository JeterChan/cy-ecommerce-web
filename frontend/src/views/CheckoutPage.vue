<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCheckoutStore } from '@/stores/useCheckoutStore'
import { storeToRefs } from 'pinia'
import OrderSummary from '@/components/Checkout/OrderSummary.vue'
import PurchaserForm from '@/components/Checkout/PurchaserForm.vue'
import ShippingForm from '@/components/Checkout/ShippingForm.vue'
import PaymentMethod from '@/components/Checkout/PaymentMethod.vue'
import { useCheckoutValidation } from '@/composables/useCheckoutValidation'

const router = useRouter()
const store = useCheckoutStore()
const { purchaser, shipping, payment, orderNote, isSubmitting, error } = storeToRefs(store)
const { errors, validatePurchaser, validateShipping, clearErrors } = useCheckoutValidation()

// For MVP, we might initialize with dummy data if cart is empty, 
// or expect data to be passed via state management from Cart.
// Here we'll ensure there's something to see for development.
onMounted(() => {
  if (store.items.length === 0) {
    store.setItems([
      { id: '1', name: '測試商品 A', price: 1000, quantity: 2 },
      { id: '2', name: '測試商品 B', price: 500, quantity: 1 }
    ])
  }
})

const handleSubmit = async () => {
  clearErrors()
  const isPurchaserValid = validatePurchaser(purchaser.value)
  const isShippingValid = validateShipping(shipping.value)
  
  if (!isPurchaserValid || !isShippingValid) {
    // Scroll to top or first error could be added here
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }

  try {
    const order = await store.submitOrder()
    router.push({ path: '/order-success', query: { orderId: order.id } })
  } catch (e) {
    // Error is handled in store and displayed via error ref
    console.error(e)
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">結帳</h1>
    
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
        <button 
          @click="handleSubmit"
          :disabled="isSubmitting"
          class="w-full bg-slate-900 text-white py-4 rounded-lg font-bold text-lg hover:bg-slate-800 transition-transform active:scale-[0.98] shadow-lg hover:shadow-xl mt-6 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center"
        >
          <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isSubmitting ? '處理中...' : '送出訂單' }}
        </button>
      </div>
    </div>
  </div>
</template>
