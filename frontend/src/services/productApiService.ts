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

    // 分類篩選
    if (params.categoryId) {
      queryParams.append('category_id', params.categoryId.toString())
    }

    // 只獲取上架商品
    queryParams.append('is_active', 'true')

    const url = `/api/v1/products?${queryParams.toString()}`
    console.log('📡 [Product API] GET', url)

    const response = await api.get<any[]>(url)

    // 轉換後端格式為前端格式
    const transformed = response.data.map((p: any): Product => ({
      id: p.id,
      name: p.name,
      description: p.description || '',
      price: Number(p.price),
      imageUrl: p.image_url || 'https://placehold.co/300x200?text=Product',
      tags: p.category_names || [],
      stockQuantity: p.stock_quantity,
      isLowStock: p.is_low_stock,
      is_featured: false,
      categoryIds: p.category_ids || [],
      categoryNames: p.category_names || []
    }))

    // 應用前端搜尋過濾 (如果後端尚未支援 query)
    let filtered = transformed
    if (params.query) {
      const q = params.query.toLowerCase()
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q)
      )
    }

    return {
      products: filtered,
      total: filtered.length,
      page: params.page || 1,
      limit: params.limit || filtered.length,
      pages: Math.ceil(filtered.length / (params.limit || 10))
    }
  },

  /**
   * 獲取單個產品
   */
  async getProductById(id: string): Promise<Product | undefined> {
    try {
      console.log('📡 [Product API] GET /api/v1/products/' + id)
      const response = await api.get<any>(`/api/v1/products/${id}`)

      return {
        id: response.data.id,
        name: response.data.name,
        description: response.data.description || '',
        price: Number(response.data.price),
        imageUrl: response.data.image_url || 'https://placehold.co/300x200?text=Product',
        tags: response.data.category_names || [],
        is_featured: false,
        categoryIds: response.data.category_ids || [],
        categoryNames: response.data.category_names || []
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
   * 獲取所有標籤（從分類獲取）
   */
  async getTags(): Promise<string[]> {
    const { categoryService } = await import('./categoryService')
    const categories = await categoryService.getCategories()
    return categories.map(c => c.name)
  }
}

