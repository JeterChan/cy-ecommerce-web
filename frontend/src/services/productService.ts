import type { Product, ProductListResponse, ProductSearchParams } from '@/models/Product'
import { categoryService } from './categoryService'

// Mock Data
// Updated tags to match CategoryService names exactly
const mockProducts: Product[] = [
  {
    id: '1',
    name: '智慧型手機 X',
    description: '最新的智慧型手機，擁有強大的處理器與相機。',
    price: 29900,
    imageUrl: 'https://placehold.co/300x200?text=Phone',
    tags: ['3C 數位', '手機'],
    is_featured: true,
    categoryId: 'c1-1'
  },
  {
    id: '2',
    name: '藍牙耳機 Pro',
    description: '主動降噪，高音質無線耳機。',
    price: 5990,
    imageUrl: 'https://placehold.co/300x200?text=Headphone',
    tags: ['3C 數位', '耳機'],
    is_featured: true,
    categoryId: 'c1-2'
  },
  {
    id: '3',
    name: '純棉T恤',
    description: '舒適透氣，百分之百純棉。',
    price: 490,
    imageUrl: 'https://placehold.co/300x200?text=T-Shirt',
    tags: ['流行服飾', '男裝'],
    categoryId: 'c2-1'
  },
  {
    id: '4',
    name: '多功能背包',
    description: '防水耐磨，適合旅行與日常使用。',
    price: 1290,
    imageUrl: 'https://placehold.co/300x200?text=Bag',
    tags: ['流行服飾', '配件'],
    is_featured: true,
    categoryId: 'c2-2'
  },
  {
    id: '5',
    name: '機械鍵盤',
    description: '青軸手感，RGB背光。',
    price: 2490,
    imageUrl: 'https://placehold.co/300x200?text=Keyboard',
    tags: ['3C 數位', '電腦周邊'], // Note: '電腦周邊' isn't in mockCategories (it has '電腦'), so this tag might need adjustment or is just an extra tag.
    categoryId: 'c1-3'
  },
  {
    id: '6',
    name: '高級咖啡機',
    description: '一鍵式操作，享受專業級咖啡。',
    price: 8990,
    imageUrl: 'https://placehold.co/300x200?text=CoffeeMachine',
    tags: ['生活家電', '廚房家電'],
    is_featured: true,
    categoryId: 'c3-1'
  },
  {
    id: '7',
    name: '智能手環',
    description: '追蹤您的健康與運動數據。',
    price: 1590,
    imageUrl: 'https://placehold.co/300x200?text=SmartBand',
    tags: ['3C 數位', '穿戴裝置'],
    is_featured: true,
    categoryId: 'c1-4'
  },
  {
    id: '8',
    name: '無線充電板',
    description: '兼容多款手機，快速無線充電。',
    price: 790,
    imageUrl: 'https://placehold.co/300x200?text=WirelessCharger',
    tags: ['3C 數位', '手機配件'],
    is_featured: true,
    categoryId: 'c1'
  },
  {
    id: '9',
    name: '舒適懶人沙發',
    description: '符合人體工學，享受放鬆時光。',
    price: 3500,
    imageUrl: 'https://placehold.co/300x200?text=Sofa',
    tags: ['家居生活', '生活家電'], // Adjusted '傢俱' -> '家居生活'
    categoryId: 'c4'
  },
  {
    id: '10',
    name: '專業運動鞋',
    description: '輕量透氣，提供卓越的支撐。',
    price: 2800,
    imageUrl: 'https://placehold.co/300x200?text=Sneakers',
    tags: ['流行服飾', '運動服飾'], // Adjusted '運動' -> '運動服飾'
    categoryId: 'c2-3'
  },
  {
    id: '11',
    name: '多功能電烤箱',
    description: '烘焙、燒烤一機搞定。',
    price: 4500,
    imageUrl: 'https://placehold.co/300x200?text=Oven',
    tags: ['生活家電', '廚房家電'],
    is_featured: true,
    categoryId: 'c3-1'
  },
  {
    id: '12',
    name: '高質感錢包',
    description: '真皮材質，多卡位設計。',
    price: 1800,
    imageUrl: 'https://placehold.co/300x200?text=Wallet',
    tags: ['流行服飾', '配件'],
    is_featured: true,
    categoryId: 'c2-2'
  },
  {
    id: '13',
    name: '超輕薄筆記型電腦',
    description: '強大效能，隨身攜帶。',
    price: 35900,
    imageUrl: 'https://placehold.co/300x200?text=Laptop',
    tags: ['3C 數位', '電腦'],
    categoryId: 'c1-3'
  },
  {
    id: '14',
    name: '電競滑鼠',
    description: '高DPI，精準定位。',
    price: 1290,
    imageUrl: 'https://placehold.co/300x200?text=Mouse',
    tags: ['3C 數位', '電腦周邊'],
    categoryId: 'c1-3'
  },
  {
    id: '15',
    name: '抗藍光眼鏡',
    description: '保護眼睛，減緩疲勞。',
    price: 990,
    imageUrl: 'https://placehold.co/300x200?text=Glasses',
    tags: ['流行服飾', '配件'],
    categoryId: 'c2-2'
  },
  {
    id: '16',
    name: '空氣清淨機',
    description: '有效過濾PM2.5，還你清新空氣。',
    price: 4990,
    imageUrl: 'https://placehold.co/300x200?text=AirPurifier',
    tags: ['生活家電', '生活家電'], // Tag repetition intentional for matching
    categoryId: 'c3-2'
  },
  {
    id: '17',
    name: '吸塵器',
    description: '強大吸力，清潔無死角。',
    price: 6990,
    imageUrl: 'https://placehold.co/300x200?text=Vacuum',
    tags: ['生活家電', '清潔'], // '清潔' not in categories but OK
    categoryId: 'c3-2'
  },
  {
    id: '18',
    name: '瑜珈墊',
    description: '加厚防滑，適合各種瑜珈動作。',
    price: 690,
    imageUrl: 'https://placehold.co/300x200?text=YogaMat',
    tags: ['戶外運動', '健身器材'],
    categoryId: 'c5-1'
  },
  {
    id: '19',
    name: '運動水壺',
    description: '大容量，耐摔材質。',
    price: 390,
    imageUrl: 'https://placehold.co/300x200?text=WaterBottle',
    tags: ['戶外運動', '配件'],
    categoryId: 'c5-1'
  },
  {
    id: '20',
    name: '簡約風格檯燈',
    description: '護眼燈光，可調節亮度。',
    price: 890,
    imageUrl: 'https://placehold.co/300x200?text=Lamp',
    tags: ['家居生活', '燈具'],
    categoryId: 'c4-1'
  },
  {
    id: '21',
    name: '人體工學椅',
    description: '久坐不累，保護脊椎。',
    price: 5990,
    imageUrl: 'https://placehold.co/300x200?text=Chair',
    tags: ['家居生活', '辦公家具'],
    categoryId: 'c4-2'
  },
  {
    id: '22',
    name: '真皮皮帶',
    description: '經典款式，百搭耐用。',
    price: 790,
    imageUrl: 'https://placehold.co/300x200?text=Belt',
    tags: ['流行服飾', '配件'],
    categoryId: 'c2-2'
  },
  {
    id: '23',
    name: '休閒長褲',
    description: '舒適修身，適合各種場合。',
    price: 890,
    imageUrl: 'https://placehold.co/300x200?text=Pants',
    tags: ['流行服飾', '男裝'],
    categoryId: 'c2-1'
  },
  {
    id: '24',
    name: '連帽外套',
    description: '保暖時尚，秋冬必備。',
    price: 1590,
    imageUrl: 'https://placehold.co/300x200?text=Hoodie',
    tags: ['流行服飾', '男裝'],
    categoryId: 'c2-1'
  },
  {
    id: '25',
    name: '藍牙音響',
    description: '360度環繞音效，防水設計。',
    price: 2290,
    imageUrl: 'https://placehold.co/300x200?text=Speaker',
    tags: ['3C 數位', '音響'],
    categoryId: 'c1'
  },
  {
    id: '26',
    name: '拍立得相機',
    description: '即拍即得，紀錄美好時刻。',
    price: 2990,
    imageUrl: 'https://placehold.co/300x200?text=Camera',
    tags: ['3C 數位', '相機'],
    categoryId: 'c1'
  },
  {
    id: '27',
    name: '微波爐',
    description: '快速加熱，方便實用。',
    price: 2500,
    imageUrl: 'https://placehold.co/300x200?text=Microwave',
    tags: ['生活家電', '廚房家電'],
    categoryId: 'c3-1'
  },
  {
    id: '28',
    name: '果汁機',
    description: '新鮮果汁，健康生活。',
    price: 1200,
    imageUrl: 'https://placehold.co/300x200?text=Juicer',
    tags: ['生活家電', '廚房家電'],
    categoryId: 'c3-1'
  },
  {
    id: '29',
    name: '登山鞋',
    description: '防水透氣，抓地力強。',
    price: 3500,
    imageUrl: 'https://placehold.co/300x200?text=HikingShoes',
    tags: ['流行服飾', '戶外運動'], // '運動' -> '戶外運動'
    categoryId: 'c5-2'
  },
  {
    id: '30',
    name: '露營帳篷',
    description: '輕量化設計，快速搭建。',
    price: 4500,
    imageUrl: 'https://placehold.co/300x200?text=Tent',
    tags: ['戶外運動', '露營用品'],
    categoryId: 'c5-2'
  },
  {
    id: '31',
    name: '行動電源',
    description: '大容量，支援快充。',
    price: 990,
    imageUrl: 'https://placehold.co/300x200?text=PowerBank',
    tags: ['3C 數位', '手機配件'],
    categoryId: 'c1'
  },
  {
    id: '32',
    name: '平板電腦',
    description: '輕薄便攜，影音娛樂首選。',
    price: 12900,
    imageUrl: 'https://placehold.co/300x200?text=Tablet',
    tags: ['3C 數位', '電腦'],
    categoryId: 'c1-3'
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

    if (params.tags && params.tags.length > 0) {
      // Filter products that have AT LEAST ONE of the selected tags
      filtered = filtered.filter(p => p.tags.some(t => params.tags!.includes(t)))
    } else if (params.tag) {
      // Logic with hierarchy support
      const allCategories = await categoryService.getTree()
      const category = allCategories.find(c => c.name === params.tag)
      
      const searchTags = [params.tag]
      if (category) {
        // Find all children
        const children = allCategories.filter(c => c.parentId === category.id)
        children.forEach(c => searchTags.push(c.name))
      }

      // Filter products that have ANY of the related tags
      filtered = filtered.filter(p => p.tags.some(t => searchTags.includes(t!)))
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

  async getFeaturedProducts(): Promise<Product[]> {
    await new Promise(resolve => setTimeout(resolve, 300))
    return mockProducts.filter(p => p.is_featured)
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
