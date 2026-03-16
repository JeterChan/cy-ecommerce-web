/**
 * Admin Product API Service
 *
 * 管理員專用的商品管理 API
 */
import { api } from '@/lib/api'
import type { 
  Product, 
  ProductListResponse, 
  AdminProductCreate, 
  AdminProductUpdate,
  AdminProductListParams,
} from '@/models/Product'

function transformProduct(p: any): Product {
  return {
    id: p.id,
    name: p.name,
    description: p.description || '',
    price: Number(p.price),
    imageUrl: p.image_url || 'https://placehold.co/300x200?text=Product',
    tags: [],
    stockQuantity: p.stock_quantity,
    isActive: p.is_active,
    isLowStock: p.is_low_stock,
    categoryIds: p.category_ids || [],
    categoryNames: p.category_names || [],
    imageUrls: p.images?.map((img: any) => img.url) || [],
    images: p.images?.map((img: any) => ({
      url: img.url,
      is_primary: img.is_primary
    })) || [],
    createdAt: p.created_at,
  }
}

export const adminProductService = {
  /**
   * 獲取產品列表 (管理員用，含搜尋/分類篩選/排序/分頁)
   */
  async getAdminProducts(params: AdminProductListParams = {}): Promise<ProductListResponse> {
    const queryParams = new URLSearchParams()
    if (params.page !== undefined) queryParams.append('page', params.page.toString())
    if (params.limit !== undefined) queryParams.append('limit', params.limit.toString())
    if (params.search) queryParams.append('search', params.search)
    if (params.category_id != null) queryParams.append('category_id', params.category_id.toString())
    if (params.sort) queryParams.append('sort', params.sort)

    const url = `/api/v1/admin/products?${queryParams.toString()}`
    const response = await api.get<any>(url)
    const data = response.data

    return {
      products: (data.products || []).map(transformProduct),
      total: data.total ?? 0,
      page: data.page ?? 1,
      limit: data.limit ?? 10,
      pages: data.pages ?? 1,
    }
  },

  /**
   * 建立產品
   */
  async createProduct(data: AdminProductCreate): Promise<Product> {
    const response = await api.post('/api/v1/admin/products', data)
    return transformProduct(response.data)
  },

  /**
   * 更新產品
   */
  async updateProduct(id: string, data: AdminProductUpdate): Promise<Product> {
    const response = await api.put(`/api/v1/admin/products/${id}`, data)
    return transformProduct(response.data)
  },

  /**
   * 刪除產品
   */
  async deleteProduct(id: string): Promise<void> {
    await api.delete(`/api/v1/admin/products/${id}`)
  },

  /**
   * 獲取 S3 預簽名 URL
   */
  async getPresignedUrl(filename: string, contentType: string): Promise<{ upload_url: string; image_url: string }> {
    const response = await api.post('/api/v1/admin/products/images/presign', {
      filename,
      content_type: contentType
    })
    return response.data
  }
}

