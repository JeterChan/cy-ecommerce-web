import type { Category } from '@/models/Category'

const mockCategories: Category[] = [
  { id: 'c1', name: '3C 數位', slug: '3c', parentId: undefined },
  { id: 'c1-1', name: '手機', slug: 'phones', parentId: 'c1' },
  { id: 'c1-2', name: '耳機', slug: 'headphones', parentId: 'c1' },
  { id: 'c1-3', name: '電腦', slug: 'computers', parentId: 'c1' },
  { id: 'c1-4', name: '穿戴裝置', slug: 'wearables', parentId: 'c1' },
  
  { id: 'c2', name: '流行服飾', slug: 'fashion', parentId: undefined },
  { id: 'c2-1', name: '男裝', slug: 'men', parentId: 'c2' },
  { id: 'c2-2', name: '配件', slug: 'accessories', parentId: 'c2' },
  { id: 'c2-3', name: '運動服飾', slug: 'sportswear', parentId: 'c2' },

  { id: 'c3', name: '生活家電', slug: 'appliances', parentId: undefined },
  { id: 'c3-1', name: '廚房家電', slug: 'kitchen', parentId: 'c3' },
  { id: 'c3-2', name: '生活家電', slug: 'living', parentId: 'c3' },

  { id: 'c4', name: '家居生活', slug: 'home-living', parentId: undefined },
  { id: 'c4-1', name: '燈具', slug: 'lighting', parentId: 'c4' },
  { id: 'c4-2', name: '辦公家具', slug: 'office', parentId: 'c4' },
  
  { id: 'c5', name: '戶外運動', slug: 'outdoors', parentId: undefined },
  { id: 'c5-1', name: '健身器材', slug: 'fitness', parentId: 'c5' },
  { id: 'c5-2', name: '露營用品', slug: 'camping', parentId: 'c5' }
]

export const categoryService = {
  async getTree(): Promise<Category[]> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100))
    return [...mockCategories]
  },

  async getById(id: string): Promise<Category | undefined> {
    await new Promise(resolve => setTimeout(resolve, 50))
    return mockCategories.find(c => c.id === id)
  }
}
