import type { Product, ProductListResponse, ProductSearchParams } from '@/models/Product'
import { productApiService } from './productApiService'

export const productService = {
  async getProducts(params: ProductSearchParams = {}): Promise<ProductListResponse> {
    console.log('🌐 [ProductService] 獲取產品列表')
    return await productApiService.getProducts(params)
  },

  async getFeaturedProducts(): Promise<Product[]> {
    console.log('🌐 [ProductService] 獲取精選產品')
    return await productApiService.getFeaturedProducts()
  },

  async getProductById(id: string): Promise<Product | undefined> {
    console.log('🌐 [ProductService] 獲取產品詳情:', id)
    return await productApiService.getProductById(id)
  },

  async getTags(): Promise<string[]> {
    console.log('🌐 [ProductService] 獲取標籤列表')
    return await productApiService.getTags()
  }
}
