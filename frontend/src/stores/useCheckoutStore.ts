import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ShippingMethod, PaymentMethod, PaymentStatus, type PurchaserInfo, type ShippingInfo, type PaymentInfo } from '@/types/orderInfo'
import { api } from '@/lib/api'
import { useCartStore } from './cart'

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
    method: PaymentMethod.COD,
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

    console.log('🚀 [Checkout] 開始送出訂單...')
    console.log('📦 [Checkout] 訂單商品數量:', items.value.length)
    console.log('📦 [Checkout] 訂單商品明細:', JSON.stringify(items.value, null, 2))
    console.log('👤 [Checkout] 購買人資訊:', purchaser.value)
    console.log('🚚 [Checkout] 運送資訊:', shipping.value)
    console.log('💳 [Checkout] 付款資訊:', payment.value)
    console.log('📝 [Checkout] 訂單備註:', orderNote.value)

    // ⚠️ 關鍵檢查：確保有商品
    if (items.value.length === 0) {
      console.error('❌ [Checkout] 訂單商品為空，無法建立訂單')
      error.value = '購物車是空的，無法建立訂單'
      isSubmitting.value = false
      throw new Error('購物車是空的')
    }

    // 檢查是否有登入 token
    const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken')
    console.log('🔑 [Checkout] 認證 Token:', token ? '存在' : '不存在')

    if (!token) {
      console.error('❌ [Checkout] 使用者未登入，無法建立訂單')
      error.value = '請先登入後再進行結帳'
      isSubmitting.value = false
      throw new Error('使用者未登入')
    }

    // 🔍 檢查購物車同步狀態
    const cartStore = useCartStore()
    console.log('🔍 [Checkout] 檢查購物車同步狀態...')
    console.log('🛒 [Checkout] Cart Store 商品數量:', cartStore.items.length)
    console.log('🛒 [Checkout] Cart Store 商品:', JSON.stringify(cartStore.items, null, 2))

    // ⚠️ 重要：確保購物車已同步到後端
    if (cartStore.items.length === 0) {
      console.error('❌ [Checkout] Cart Store 是空的，可能購物車未同步')
      error.value = '購物車數據異常，請重新整理頁面'
      isSubmitting.value = false
      throw new Error('Cart Store 是空的')
    }

    try {
      // 🔑 關鍵：準備新的請求資料格式，符合 /api/v1/orders/checkout 的 CheckoutRequest
      const requestData = {
        recipient_name: shipping.value.recipient_name || purchaser.value.name,
        recipient_phone: shipping.value.recipient_phone || purchaser.value.phone,
        shipping_address: shipping.value.address || '無地址', // 後端 validation 可能需要
        payment_method: payment.value.method // 使用前端選擇的付款方式
      }

      console.log('📡 [Checkout] 呼叫新 API: POST /api/v1/orders/checkout')
      console.log('📤 [Checkout] 請求資料:', JSON.stringify(requestData, null, 2))

      const response = await api.post('/api/v1/orders/checkout', requestData)

      console.log('✅ [Checkout] 交易式結帳成功:', response.data)
      console.log('📋 [Checkout] 訂單 ID:', response.data.id)
      console.log('💰 [Checkout] 訂單總額:', response.data.total_amount)

      const order = response.data

      // 成功後清空本地購物車狀態 (後端購物車已經在 API 中被清空)
      console.log('🗑️ [Checkout] 清空本地購物車狀態...')
      await cartStore.clearCart()

      // 清空 checkout 的 items
      items.value = []

      console.log('✨ [Checkout] 結帳流程完成')

      return order
    } catch (e: any) {
      console.error('❌ [Checkout] 訂單建立失敗:', e)
      console.error('❌ [Checkout] 錯誤狀態碼:', e.response?.status)
      console.error('❌ [Checkout] 錯誤詳情:', e.response?.data || e.message)
      console.error('❌ [Checkout] 完整錯誤:', JSON.stringify(e.response?.data, null, 2))

      // 根據錯誤類型提供更明確的訊息
      if (e.response?.status === 404) {
        error.value = 'API 路徑錯誤，請聯繫技術支援'
      } else if (e.response?.status === 401) {
        error.value = '登入已過期，請重新登入'
      } else if (e.response?.status === 400) {
        const detail = e.response?.data?.detail
        // 檢查是否是購物車為空的錯誤
        if (typeof detail === 'string' && detail.includes('購物車')) {
          error.value = '購物車是空的，請先加入商品。可能是購物車未同步到後端，請重新整理頁面後再試。'
          console.error('❌ [Checkout] 後端回報購物車為空！')
          console.error('💡 [Checkout] 建議：檢查購物車是否已正確同步到後端（Redis/DB）')
        } else {
          error.value = detail || '訂單資料有誤，請檢查後重試'
        }
      } else {
        error.value = e.response?.data?.detail || '結帳失敗，請稍後再試'
      }

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
