/**
 * Product API Service
 *
 * 從後端 API 獲取產品數據
 */
import { api } from '@/lib/api'
import type { Product, ProductListResponse, ProductSearchParams } from '@/models/Product'

export const productApiService = {
  /**
   * 獲取產品列表
   */
  async getProducts(params: ProductSearchParams = {}): Promise<ProductListResponse> {
    const queryParams = new URLSearchParams()

    // 分頁參數
    if (params.page) {
      const skip = (params.page - 1) * (params.limit || 10)
      queryParams.append('skip', skip.toString())
    }
    if (params.limit) {
      queryParams.append('limit', params.limit.toString())
    }

    // 只獲取上架商品
    queryParams.append('is_active', 'true')

    const url = `/api/v1/products?${queryParams.toString()}`
    console.log('📡 [Product API] GET', url)

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await api.get<any[]>(url)

    // 轉換後端格式為前端格式
    const transformed = response.data.map((p: any): Product => ({
      id: p.id,
      name: p.name,
      description: p.description || '',
      price: Number(p.price),
      imageUrl: p.image_url || 'https://placehold.co/300x200?text=Product',
      tags: [], // TODO: 從 category_ids 轉換
      is_featured: false // TODO: 從後端獲取
    }))

    // 應用前端過濾
    let filtered = transformed

    // 搜尋過濾
    if (params.query) {
      const q = params.query.toLowerCase()
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q)
      )
    }

    // 標籤過濾（目前無法實現，需要後端支援）
    // if (params.tag || params.tags) {
    //   // 等待後端實現 tag 過濾
    // }

    return {
      products: filtered,
      total: filtered.length,
      page: params.page || 1,
      limit: params.limit || filtered.length
    }
  },

  /**
   * 獲取單個產品
   */
  async getProductById(id: string): Promise<Product | undefined> {
    try {
      console.log('📡 [Product API] GET /api/v1/products/' + id)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const response = await api.get<any>(`/api/v1/products/${id}`)

      return {
        id: response.data.id,
        name: response.data.name,
        description: response.data.description || '',
        price: Number(response.data.price),
        imageUrl: response.data.image_url || 'https://placehold.co/300x200?text=Product',
        tags: [],
        is_featured: false
      }
    } catch (error) {
      console.error('❌ [Product API] 獲取產品失敗:', error)
      return undefined
    }
  },

  /**
   * 獲取精選產品（目前從所有產品中取前 8 個）
   */
  async getFeaturedProducts(): Promise<Product[]> {
    const response = await this.getProducts({ limit: 8 })
    return response.products
  },

  /**
   * 獲取所有標籤（暫時返回空陣列，等待後端實現）
   */
  async getTags(): Promise<string[]> {
    // TODO: 實現從後端獲取分類/標籤
    return ['3C 數位', '流行服飾', '生活家電', '家居生活', '戶外運動']
  }
}

