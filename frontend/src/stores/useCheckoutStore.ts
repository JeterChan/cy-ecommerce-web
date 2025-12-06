import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ShippingMethod, PaymentMethod, PaymentStatus, type PurchaserInfo, type ShippingInfo, type PaymentInfo } from '@/types/orderInfo'
import { createOrder } from '@/services/mockOrderService'

export const useCheckoutStore = defineStore('checkout', () => {
  const items = ref<any[]>([])
  const purchaser = ref<PurchaserInfo>({ name: '', phone: '', email: '' })
  const shipping = ref<ShippingInfo>({ 
    recipient_name: '', 
    recipient_phone: '', 
    method: ShippingMethod.HOME_DELIVERY, 
    address: '', 
    store_name: '' 
  })
  const payment = ref<PaymentInfo>({
    method: PaymentMethod.CREDIT_CARD,
    status: PaymentStatus.UNPAID
  })
  const orderNote = ref('')
  const isSubmitting = ref(false)
  const error = ref('')
  
  const totalAmount = computed(() => {
    return items.value.reduce((total, item: any) => total + (item.price * item.quantity), 0)
  })

  const setItems = (cartItems: any[]) => {
    items.value = cartItems
  }

  const submitOrder = async () => {
    isSubmitting.value = true
    error.value = ''
    try {
      const order = await createOrder(
        items.value,
        purchaser.value,
        shipping.value,
        payment.value,
        orderNote.value
      )
      // Success: Clear cart (simulate)
      items.value = []
      return order
    } catch (e: any) {
      error.value = '結帳失敗，請稍後再試'
      throw e
    } finally {
      isSubmitting.value = false
    }
  }

  return {
    items,
    totalAmount,
    setItems,
    purchaser,
    shipping,
    payment,
    orderNote,
    isSubmitting,
    error,
    submitOrder
  }
})
