import type { Category } from '@/models/Category'
import { api } from '@/lib/api'

export interface AdminCategory {
  id: number
  name: string
  slug: string
}

export const categoryService = {
  /** 獲取所有公開分類 (用於前台) */
  async getCategories(): Promise<Category[]> {
    const response = await api.get<AdminCategory[]>('/api/v1/products/categories')
    return response.data.map(c => ({
      id: c.id.toString(),
      name: c.name,
      slug: c.slug
    }))
  },

  /** 獲取分類樹 (暫時扁平化回傳，後續若有 parentId 再實作樹狀) */
  async getTree(): Promise<Category[]> {
    return this.getCategories()
  },

  async getById(id: string): Promise<Category | undefined> {
    const categories = await this.getCategories()
    return categories.find(c => c.id === id)
  },

  /** 管理員：從後端取得真實分類列表 */
  async getAdminCategories(): Promise<AdminCategory[]> {
    const response = await api.get<AdminCategory[]>('/api/v1/admin/categories')
    return response.data
  },

  /** 管理員：新增分類 */
  async createCategory(data: { name: string; slug: string }): Promise<AdminCategory> {
    const response = await api.post<AdminCategory>('/api/v1/admin/categories', data)
    return response.data
  },

  /** 管理員：刪除分類 */
  async deleteCategory(id: number): Promise<void> {
    await api.delete(`/api/v1/admin/categories/${id}`)
  }
}
