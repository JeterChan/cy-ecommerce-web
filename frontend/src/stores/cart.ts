import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { CartItem } from '../models/Cart'
import type { Product } from '../models/Product'
import { cartApiService } from '@/services/cartService'
import { useAuthStore } from './auth'

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const isLoading = ref(false)
  const isSynced = ref(false) // 標記是否已從後端同步

  // Initialize from localStorage (fallback)
  const storedCart = localStorage.getItem('cart')
  if (storedCart) {
    try {
      items.value = JSON.parse(storedCart)
    } catch (e) {
      console.error('Failed to parse cart from localStorage', e)
      localStorage.removeItem('cart')
    }
  }

  // 從後端同步購物車（登入後或頁面載入時呼叫）
  async function syncFromBackend() {
    if (isSynced.value) {
      console.log('⏭️ [Cart] 已經同步過，跳過')
      return // 避免重複同步
    }

    const authStore = useAuthStore()

    // 如果未登入，不需要同步
    if (!authStore.isAuthenticated) {
      console.log('👤 [Cart] 未登入，跳過後端同步')
      isSynced.value = true
      return
    }

    try {
      console.log('🔄 [Cart] 從後端同步購物車...')
      const backendItems = await cartApiService.getCart()

      // ✅ 直接使用後端資料，不進行累加
      // 因為後端已經是最新的購物車狀態
      const newItems: CartItem[] = backendItems.map(item => ({
        productId: item.product_id,
        name: item.product_name,
        price: item.unit_price,
        imageUrl: item.image_url || '',
        quantity: item.quantity
      }))

      items.value = newItems
      localStorage.setItem('cart', JSON.stringify(items.value))

      isSynced.value = true
      console.log('✅ [Cart] 購物車同步完成，共', items.value.length, '項商品')
    } catch (error) {
      console.warn('⚠️ [Cart] 同步購物車失敗，使用本地資料:', error)
      // 如果同步失敗，繼續使用 localStorage 的資料
      isSynced.value = true // 標記為已同步，避免重試
    }
  }

  // Persistence to localStorage
  watch(items, (newItems) => {
    localStorage.setItem('cart', JSON.stringify(newItems))
  }, { deep: true })

  // Getters
  const totalQuantity = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  const totalAmount = computed(() => {
    return items.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  })

  // Actions
  async function addToCart(product: Product, quantity: number) {
    isLoading.value = true

    try {
      console.log('🛒 [Cart] 加入購物車:', product.name, 'x', quantity)
      console.log('🔍 [Cart] 商品 ID:', product.id)

      const authStore = useAuthStore()

      // 🔐 只有登入用戶才同步到後端
      if (authStore.isAuthenticated) {
        try {
          await cartApiService.addToCart(product.id, quantity)
          console.log('✅ [Cart] 後端同步成功（會員）')
        } catch (apiError: any) {
          // 詳細記錄錯誤
          console.error('❌ [Cart] 後端同步失敗！')
          console.error('❌ [Cart] 錯誤狀態碼:', apiError.response?.status)
          console.error('❌ [Cart] 錯誤訊息:', apiError.response?.data)
          console.error('❌ [Cart] 錯誤詳情:', apiError.message)
          console.warn('⚠️ [Cart] 降級到僅本地模式（資料不會同步到後端）')

          // 如果是認證錯誤，警告使用者
          if (apiError.response?.status === 401) {
            console.warn('⚠️ [Cart] 認證失敗：可能需要重新登入')
          }
        }
      } else {
        console.log('👤 [Cart] 訪客模式：僅使用 localStorage，不同步到後端')
      }

      // 更新本地狀態（無論後端是否成功）
      const existingItem = items.value.find(item => item.productId === product.id)
      if (existingItem) {
        existingItem.quantity += quantity
      } else {
        items.value.push({
          productId: product.id,
          name: product.name,
          price: product.price,
          imageUrl: product.imageUrl,
          quantity: quantity
        })
      }

      console.log('✅ [Cart] 本地購物車更新成功，目前商品數:', items.value.length)
    } catch (error) {
      console.error('❌ [Cart] 加入購物車失敗:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function removeFromCart(productId: string) {
    isLoading.value = true

    try {
      console.log('🗑️ [Cart] 移除商品:', productId)

      const authStore = useAuthStore()

      // 🔐 只有登入用戶才同步到後端
      if (authStore.isAuthenticated) {
        try {
          await cartApiService.removeFromCart(productId)
          console.log('✅ [Cart] 後端同步成功（會員）')
        } catch (apiError) {
          console.warn('⚠️ [Cart] 後端同步失敗，僅更新本地狀態:', apiError)
        }
      } else {
        console.log('👤 [Cart] 訪客模式：僅更新本地 localStorage')
      }

      // 更新本地狀態（無論後端是否成功）
      const index = items.value.findIndex(item => item.productId === productId)
      if (index > -1) {
        items.value.splice(index, 1)
      }

      console.log('✅ [Cart] 移除商品成功')
    } catch (error) {
      console.error('❌ [Cart] 移除商品失敗:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function updateQuantity(productId: string, quantity: number) {
    isLoading.value = true

    try {
      console.log('🔄 [Cart] 更新數量:', productId, quantity)

      if (quantity <= 0) {
        await removeFromCart(productId)
        return
      }

      const authStore = useAuthStore()

      // 🔐 只有登入用戶才同步到後端
      if (authStore.isAuthenticated) {
        try {
          await cartApiService.updateCartItem(productId, quantity)
          console.log('✅ [Cart] 後端同步成功（會員）')
        } catch (apiError) {
          console.warn('⚠️ [Cart] 後端同步失敗，僅更新本地狀態:', apiError)
        }
      } else {
        console.log('👤 [Cart] 訪客模式：僅更新本地 localStorage')
      }

      // 更新本地狀態（無論後端是否成功）
      const item = items.value.find(item => item.productId === productId)
      if (item) {
        item.quantity = quantity
      }

      console.log('✅ [Cart] 更新數量成功')
    } catch (error) {
      console.error('❌ [Cart] 更新數量失敗:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function clearCart() {
    isLoading.value = true

    try {
      console.log('🗑️ [Cart] 清空購物車...')

      const authStore = useAuthStore()
      
      // 只有認證用戶才需要調用後端 API
      if (authStore.isAuthenticated) {
        try {
          await cartApiService.clearCart()
          console.log('✅ [Cart] 後端購物車清空成功')
        } catch (error) {
          console.warn('⚠️ [Cart] 後端購物車清空失敗:', error)
          // 後端失敗不影響本地清空
        }
      } else {
        console.log('👤 [Cart] 訪客用戶，只清空本地購物車')
      }

      // 更新本地狀態
      items.value = []

      console.log('✅ [Cart] 清空購物車成功')
    } catch (error) {
      console.error('❌ [Cart] 清空購物車失敗:', error)
      // 即使出錯，也清空本地購物車
      items.value = []
    } finally {
      isLoading.value = false
    }
  }

  const clearCartLocal = (): void => {
    console.log('🗑️ [Cart] 清空本地購物車（登出）')
    items.value = []
    localStorage.removeItem('cart')
  }

  const resetSync = (): void => {
    console.log('🔄 [Cart] 重置同步標記')
    isSynced.value = false
  }

  const mergeGuestCart = async (): Promise<boolean> => {
    console.log('🔄 [Cart] 開始合併訪客購物車...')
    
    isLoading.value = true
    try {
      // 取得本地訪客購物車（在登入前的購物車）
      const guestItems = items.value

      if (guestItems.length === 0) {
        console.log('ℹ️ [Cart] 訪客購物車為空，無需合併')
        // 清空本地（因為登出時已清空），重新同步用戶購物車
        await syncFromBackend()
        return true
      }

      // 轉換格式以便後端合併
      const itemsToMerge = guestItems.map(item => ({
        product_id: item.productId,
        quantity: item.quantity
      }))

      // 呼叫後端合併 API
      const mergedItems = await cartApiService.mergeCart(itemsToMerge)

      // 清空本地購物車（移除訪客商品）
      items.value = []
      localStorage.removeItem('cart')

      // 同步後端的合併結果到本地
      const newItems: CartItem[] = mergedItems.map(item => ({
        productId: item.product_id,
        name: item.product_name || `Product ${item.product_id}`,
        price: item.unit_price || 0,
        imageUrl: item.image_url || '',
        quantity: item.quantity
      }))

      items.value = newItems
      localStorage.setItem('cart', JSON.stringify(items.value))
      isSynced.value = true

      console.log('✅ [Cart] 購物車合併完成，共', items.value.length, '項商品')
      return true
    } catch (error) {
      console.error('❌ [Cart] 購物車合併失敗:', error)
      // 合併失敗，使用原本的後端購物車
      await syncFromBackend()
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    items,
    isLoading,
    totalQuantity,
    totalAmount,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    clearCartLocal,
    syncFromBackend,
    resetSync,
    mergeGuestCart
  }
})
