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

    if (params.categoryIds && params.categoryIds.length > 0) {
      params.categoryIds.forEach(id => {
        queryParams.append('category_ids', id.toString())
      })
    }

    // 只獲取上架商品
    queryParams.append('is_active', 'true')

    const url = `/api/v1/products?${queryParams.toString()}`
    console.log('📡 [Product API] GET', url)

    const response = await api.get<any>(url)
    const data = response.data || {}
    
    // 驗證回傳結構，確保 items 是陣列且 total 是數字
    const backendItems = Array.isArray(data.items) ? data.items : []
    const totalCount = typeof data.total === 'number' ? data.total : backendItems.length

    // 轉換後端格式為前端格式，增加欄位防護
    const transformed = backendItems.map((p: any): Product => ({
      id: p?.id || '',
      name: p?.name || '未命名商品',
      description: p?.description || '',
      price: (typeof p?.price === 'number' || typeof p?.price === 'string') ? Number(p.price) : 0,
      imageUrl: p?.image_url || 'https://placehold.co/300x200?text=Product',
      tags: Array.isArray(p?.category_names) ? p.category_names : [],
      stockQuantity: typeof p?.stock_quantity === 'number' ? p.stock_quantity : 0,
      isLowStock: !!p?.is_low_stock,
      is_featured: false,
      categoryIds: Array.isArray(p?.category_ids) ? p.category_ids : [],
      categoryNames: Array.isArray(p?.category_names) ? p.category_names : []
    }))

    // 應用前端搜尋過濾 (如果後端尚未支援 query)
    let filtered = transformed
    if (params.query) {
      const q = params.query.toLowerCase()
      filtered = filtered.filter((p: Product) =>
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q)
      )
    }

    const limit = params.limit || 10
    return {
      products: filtered,
      total: totalCount,
      page: params.page || 1,
      limit: limit,
      pages: Math.ceil(totalCount / limit)
    }
  },

  /**
   * 獲取單個產品
   */
  async getProductById(id: string): Promise<Product | undefined> {
    try {
      console.log('📡 [Product API] GET /api/v1/products/' + id)
      const response = await api.get<any>(`/api/v1/products/${id}`)
      const data = response.data

      if (!data || !data.id) {
        console.error('❌ [Product API] 取得無效的產品資料')
        return undefined
      }

      return {
        id: data.id,
        name: data.name || '未命名商品',
        description: data.description || '',
        price: (typeof data.price === 'number' || typeof data.price === 'string') ? Number(data.price) : 0,
        imageUrl: data.image_url || 'https://placehold.co/300x200?text=Product',
        images: Array.isArray(data.images) ? data.images.map((img: any) => ({ url: img.url, is_primary: img.is_primary })) : undefined,
        tags: Array.isArray(data.category_names) ? data.category_names : [],
        is_featured: false,
        categoryIds: Array.isArray(data.category_ids) ? data.category_ids : [],
        categoryNames: Array.isArray(data.category_names) ? data.category_names : []
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

