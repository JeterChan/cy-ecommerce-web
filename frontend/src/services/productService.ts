import type { Product, ProductListResponse, ProductSearchParams } from '@/models/Product'

// Mock Data
const mockProducts: Product[] = [
  {
    id: '1',
    name: '智慧型手機 X',
    description: '最新的智慧型手機，擁有強大的處理器與相機。',
    price: 29900,
    imageUrl: 'https://placehold.co/300x200?text=Phone',
    tags: ['3C', '手機']
  },
  {
    id: '2',
    name: '藍牙耳機 Pro',
    description: '主動降噪，高音質無線耳機。',
    price: 5990,
    imageUrl: 'https://placehold.co/300x200?text=Headphone',
    tags: ['3C', '耳機']
  },
  {
    id: '3',
    name: '純棉T恤',
    description: '舒適透氣，百分之百純棉。',
    price: 490,
    imageUrl: 'https://placehold.co/300x200?text=T-Shirt',
    tags: ['服飾', '男裝']
  },
  {
    id: '4',
    name: '多功能背包',
    description: '防水耐磨，適合旅行與日常使用。',
    price: 1290,
    imageUrl: 'https://placehold.co/300x200?text=Bag',
    tags: ['服飾', '配件']
  },
  {
    id: '5',
    name: '機械鍵盤',
    description: '青軸手感，RGB背光。',
    price: 2490,
    imageUrl: 'https://placehold.co/300x200?text=Keyboard',
    tags: ['3C', '電腦周邊']
  }
]

export const productService = {
  async getProducts(params: ProductSearchParams = {}): Promise<ProductListResponse> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300))

    let filtered = [...mockProducts]

    if (params.query) {
      const q = params.query.toLowerCase()
      filtered = filtered.filter(p => 
        p.name.toLowerCase().includes(q) || 
        p.description.toLowerCase().includes(q)
      )
    }

    if (params.tag) {
      filtered = filtered.filter(p => p.tags.includes(params.tag!))
    }

    const total = filtered.length
    const page = params.page || 1
    const limit = params.limit || 10
    const start = (page - 1) * limit
    const end = start + limit
    
    const products = filtered.slice(start, end)

    return {
      products,
      total,
      page,
      limit
    }
  },

  async getProductById(id: string): Promise<Product | undefined> {
    await new Promise(resolve => setTimeout(resolve, 200))
    return mockProducts.find(p => p.id === id)
  },

  async getTags(): Promise<string[]> {
    const tags = new Set<string>()
    mockProducts.forEach(p => p.tags.forEach(t => tags.add(t)))
    return Array.from(tags)
  }
}