import { api } from '@/lib/api'

export interface CartItemAPI {
  id: string
  product_id: string
  product_name: string
  unit_price: number
  quantity: number
  subtotal: number
  image_url?: string
  created_at: string
  updated_at: string
}

export const cartApiService = {
  /**
   * 取得購物車
   */
  async getCart(): Promise<CartItemAPI[]> {
    console.log('📡 [Cart API] 呼叫 GET /api/v1/cart')
    const response = await api.get<CartItemAPI[]>('/api/v1/cart')
    console.log('✅ [Cart API] 取得購物車:', response.data)
    return response.data
  },

  /**
   * 新增商品到購物車
   */
  async addToCart(productId: string, quantity: number): Promise<CartItemAPI> {
    console.log('📡 [Cart API] 呼叫 POST /api/v1/cart/items', { product_id: productId, quantity })
    const response = await api.post<CartItemAPI>('/api/v1/cart/items', {
      product_id: productId,
      quantity
    })
    console.log('✅ [Cart API] 加入購物車成功:', response.data)
    return response.data
  },

  /**
   * 更新購物車商品數量
   */
  async updateCartItem(productId: string, quantity: number): Promise<CartItemAPI> {
    console.log('📡 [Cart API] 呼叫 PATCH /api/v1/cart/items/' + productId, { quantity })
    const response = await api.patch<CartItemAPI>(`/api/v1/cart/items/${productId}`, {
      quantity
    })
    console.log('✅ [Cart API] 更新購物車成功:', response.data)
    return response.data
  },

  /**
   * 從購物車移除商品
   */
  async removeFromCart(productId: string): Promise<void> {
    console.log('📡 [Cart API] 呼叫 DELETE /api/v1/cart/items/' + productId)
    await api.delete(`/api/v1/cart/items/${productId}`)
    console.log('✅ [Cart API] 移除購物車商品成功')
  },

  /**
   * 清空購物車
   */
  async clearCart(): Promise<void> {
    console.log('📡 [Cart API] 呼叫 DELETE /api/v1/cart')
    await api.delete('/api/v1/cart')
    console.log('✅ [Cart API] 清空購物車成功')
  }
}

