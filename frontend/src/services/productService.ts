import type { Product, ProductListResponse, ProductSearchParams } from '@/models/Product'
import { categoryService } from './categoryService'
import { productApiService } from './productApiService'

// 環境變數：是否使用後端 API（預設為 true）
const USE_BACKEND_API = import.meta.env.VITE_USE_PRODUCT_API !== 'false'

// Mock Data (作為後備)
// Updated tags to match CategoryService names exactly
// Updated IDs to UUID format to match backend API requirements
const mockProducts: Product[] = [
  {
    id: 'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d',
    name: '智慧型手機 X',
    description: '最新的智慧型手機，擁有強大的處理器與相機。',
    price: 29900,
    imageUrl: 'https://placehold.co/300x200?text=Phone',
    tags: ['3C 數位', '手機'],
    is_featured: true,
    categoryId: 'c1-1'
  },
  {
    id: 'b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e',
    name: '藍牙耳機 Pro',
    description: '主動降噪，高音質無線耳機。',
    price: 5990,
    imageUrl: 'https://placehold.co/300x200?text=Headphone',
    tags: ['3C 數位', '耳機'],
    is_featured: true,
    categoryId: 'c1-2'
  },
  {
    id: 'c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f',
    name: '純棉T恤',
    description: '舒適透氣，百分之百純棉。',
    price: 490,
    imageUrl: 'https://placehold.co/300x200?text=T-Shirt',
    tags: ['流行服飾', '男裝'],
    categoryId: 'c2-1'
  },
  {
    id: 'd4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f8a',
    name: '多功能背包',
    description: '防水耐磨，適合旅行與日常使用。',
    price: 1290,
    imageUrl: 'https://placehold.co/300x200?text=Bag',
    tags: ['流行服飾', '配件'],
    is_featured: true,
    categoryId: 'c2-2'
  },
  {
    id: 'e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b',
    name: '機械鍵盤',
    description: '青軸手感，RGB背光。',
    price: 2490,
    imageUrl: 'https://placehold.co/300x200?text=Keyboard',
    tags: ['3C 數位', '電腦周邊'],
    categoryId: 'c1-3'
  },
  {
    id: 'f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c',
    name: '高級咖啡機',
    description: '一鍵式操作，享受專業級咖啡。',
    price: 8990,
    imageUrl: 'https://placehold.co/300x200?text=CoffeeMachine',
    tags: ['生活家電', '廚房家電'],
    is_featured: true,
    categoryId: 'c3-1'
  },
  {
    id: 'a7b8c9d0-e1f2-4a3b-4c5d-6e7f8a9b0c1d',
    name: '智能手環',
    description: '追蹤您的健康與運動數據。',
    price: 1590,
    imageUrl: 'https://placehold.co/300x200?text=SmartBand',
    tags: ['3C 數位', '穿戴裝置'],
    is_featured: true,
    categoryId: 'c1-4'
  },
  {
    id: 'b8c9d0e1-f2a3-4b4c-5d6e-7f8a9b0c1d2e',
    name: '無線充電板',
    description: '兼容多款手機，快速無線充電。',
    price: 790,
    imageUrl: 'https://placehold.co/300x200?text=WirelessCharger',
    tags: ['3C 數位', '手機配件'],
    is_featured: true,
    categoryId: 'c1'
  },
  {
    id: 'c9d0e1f2-a3b4-4c5d-6e7f-8a9b0c1d2e3f',
    name: '舒適懶人沙發',
    description: '符合人體工學，享受放鬆時光。',
    price: 3500,
    imageUrl: 'https://placehold.co/300x200?text=Sofa',
    tags: ['家居生活', '生活家電'],
    categoryId: 'c4'
  },
  {
    id: 'd0e1f2a3-b4c5-4d6e-7f8a-9b0c1d2e3f4a',
    name: '專業運動鞋',
    description: '輕量透氣，提供卓越的支撐。',
    price: 2800,
    imageUrl: 'https://placehold.co/300x200?text=Sneakers',
    tags: ['流行服飾', '運動服飾'],
    categoryId: 'c2-3'
  },
  {
    id: 'e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b',
    name: '多功能電烤箱',
    description: '烘焙、燒烤一機搞定。',
    price: 4500,
    imageUrl: 'https://placehold.co/300x200?text=Oven',
    tags: ['生活家電', '廚房家電'],
    is_featured: true,
    categoryId: 'c3-1'
  },
  {
    id: 'f2a3b4c5-d6e7-4f8a-9b0c-1d2e3f4a5b6c',
    name: '高質感錢包',
    description: '真皮材質，多卡位設計。',
    price: 1800,
    imageUrl: 'https://placehold.co/300x200?text=Wallet',
    tags: ['流行服飾', '配件'],
    is_featured: true,
    categoryId: 'c2-2'
  },
  {
    id: 'a3b4c5d6-e7f8-4a9b-0c1d-2e3f4a5b6c7d',
    name: '超輕薄筆記型電腦',
    description: '強大效能，隨身攜帶。',
    price: 35900,
    imageUrl: 'https://placehold.co/300x200?text=Laptop',
    tags: ['3C 數位', '電腦'],
    categoryId: 'c1-3'
  },
  {
    id: 'b4c5d6e7-f8a9-4b0c-1d2e-3f4a5b6c7d8e',
    name: '電競滑鼠',
    description: '高DPI，精準定位。',
    price: 1290,
    imageUrl: 'https://placehold.co/300x200?text=Mouse',
    tags: ['3C 數位', '電腦周邊'],
    categoryId: 'c1-3'
  },
  {
    id: 'c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f',
    name: '抗藍光眼鏡',
    description: '保護眼睛，減緩疲勞。',
    price: 990,
    imageUrl: 'https://placehold.co/300x200?text=Glasses',
    tags: ['流行服飾', '配件'],
    categoryId: 'c2-2'
  },
  {
    id: 'd6e7f8a9-b0c1-4d2e-3f4a-5b6c7d8e9f0a',
    name: '空氣清淨機',
    description: '有效過濾PM2.5，還你清新空氣。',
    price: 4990,
    imageUrl: 'https://placehold.co/300x200?text=AirPurifier',
    tags: ['生活家電', '生活家電'],
    categoryId: 'c3-2'
  },
  {
    id: 'e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b',
    name: '吸塵器',
    description: '強大吸力，清潔無死角。',
    price: 6990,
    imageUrl: 'https://placehold.co/300x200?text=Vacuum',
    tags: ['生活家電', '清潔'],
    categoryId: 'c3-2'
  },
  {
    id: 'f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c',
    name: '瑜珈墊',
    description: '加厚防滑，適合各種瑜珈動作。',
    price: 690,
    imageUrl: 'https://placehold.co/300x200?text=YogaMat',
    tags: ['戶外運動', '健身器材'],
    categoryId: 'c5-1'
  },
  {
    id: 'a9b0c1d2-e3f4-4a5b-6c7d-8e9f0a1b2c3d',
    name: '運動水壺',
    description: '大容量，耐摔材質。',
    price: 390,
    imageUrl: 'https://placehold.co/300x200?text=WaterBottle',
    tags: ['戶外運動', '配件'],
    categoryId: 'c5-1'
  },
  {
    id: 'b0c1d2e3-f4a5-4b6c-7d8e-9f0a1b2c3d4e',
    name: '簡約風格檯燈',
    description: '護眼燈光，可調節亮度。',
    price: 890,
    imageUrl: 'https://placehold.co/300x200?text=Lamp',
    tags: ['家居生活', '燈具'],
    categoryId: 'c4-1'
  },
  {
    id: 'c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f',
    name: '人體工學椅',
    description: '久坐不累，保護脊椎。',
    price: 5990,
    imageUrl: 'https://placehold.co/300x200?text=Chair',
    tags: ['家居生活', '辦公家具'],
    categoryId: 'c4-2'
  },
  {
    id: 'd2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a',
    name: '真皮皮帶',
    description: '經典款式，百搭耐用。',
    price: 790,
    imageUrl: 'https://placehold.co/300x200?text=Belt',
    tags: ['流行服飾', '配件'],
    categoryId: 'c2-2'
  },
  {
    id: 'e3f4a5b6-c7d8-4e9f-0a1b-2c3d4e5f6a7b',
    name: '休閒長褲',
    description: '舒適修身，適合各種場合。',
    price: 890,
    imageUrl: 'https://placehold.co/300x200?text=Pants',
    tags: ['流行服飾', '男裝'],
    categoryId: 'c2-1'
  },
  {
    id: 'f4a5b6c7-d8e9-4f0a-1b2c-3d4e5f6a7b8c',
    name: '連帽外套',
    description: '保暖時尚，秋冬必備。',
    price: 1590,
    imageUrl: 'https://placehold.co/300x200?text=Hoodie',
    tags: ['流行服飾', '男裝'],
    categoryId: 'c2-1'
  },
  {
    id: 'a5b6c7d8-e9f0-4a1b-2c3d-4e5f6a7b8c9d',
    name: '藍牙音響',
    description: '360度環繞音效，防水設計。',
    price: 2290,
    imageUrl: 'https://placehold.co/300x200?text=Speaker',
    tags: ['3C 數位', '音響'],
    categoryId: 'c1'
  },
  {
    id: 'b6c7d8e9-f0a1-4b2c-3d4e-5f6a7b8c9d0e',
    name: '拍立得相機',
    description: '即拍即得，紀錄美好時刻。',
    price: 2990,
    imageUrl: 'https://placehold.co/300x200?text=Camera',
    tags: ['3C 數位', '相機'],
    categoryId: 'c1'
  },
  {
    id: 'c7d8e9f0-a1b2-4c3d-4e5f-6a7b8c9d0e1f',
    name: '微波爐',
    description: '快速加熱，方便實用。',
    price: 2500,
    imageUrl: 'https://placehold.co/300x200?text=Microwave',
    tags: ['生活家電', '廚房家電'],
    categoryId: 'c3-1'
  },
  {
    id: 'd8e9f0a1-b2c3-4d4e-5f6a-7b8c9d0e1f2a',
    name: '果汁機',
    description: '新鮮果汁，健康生活。',
    price: 1200,
    imageUrl: 'https://placehold.co/300x200?text=Juicer',
    tags: ['生活家電', '廚房家電'],
    categoryId: 'c3-1'
  },
  {
    id: 'e9f0a1b2-c3d4-4e5f-6a7b-8c9d0e1f2a3b',
    name: '登山鞋',
    description: '防水透氣，抓地力強。',
    price: 3500,
    imageUrl: 'https://placehold.co/300x200?text=HikingShoes',
    tags: ['流行服飾', '戶外運動'],
    categoryId: 'c5-2'
  },
  {
    id: 'f0a1b2c3-d4e5-4f6a-7b8c-9d0e1f2a3b4c',
    name: '露營帳篷',
    description: '輕量化設計，快速搭建。',
    price: 4500,
    imageUrl: 'https://placehold.co/300x200?text=Tent',
    tags: ['戶外運動', '露營用品'],
    categoryId: 'c5-2'
  },
  {
    id: '01b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d',
    name: '行動電源',
    description: '大容量，支援快充。',
    price: 990,
    imageUrl: 'https://placehold.co/300x200?text=PowerBank',
    tags: ['3C 數位', '手機配件'],
    categoryId: 'c1'
  },
  {
    id: '12c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e',
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
    // 🔄 使用後端 API 或 mock 數據
    if (USE_BACKEND_API) {
      try {
        console.log('🌐 [ProductService] 使用後端 API 獲取產品')
        return await productApiService.getProducts(params)
      } catch (error) {
        console.warn('⚠️ [ProductService] API 失敗，降級到 mock 數據:', error)
        // 降級到 mock
      }
    }

    // Mock 數據邏輯 (保持原有邏輯作為備援)
    console.log('📦 [ProductService] 使用 mock 數據')
    await new Promise(resolve => setTimeout(resolve, 300))

    let filtered = [...mockProducts]

    if (params.query) {
      const q = params.query.toLowerCase()
      filtered = filtered.filter(p => 
        p.name.toLowerCase().includes(q) || 
        p.description.toLowerCase().includes(q)
      )
    }

    if (params.categoryId) {
      const categoryIdStr = params.categoryId.toString()
      filtered = filtered.filter(p => p.categoryId === categoryIdStr)
    }

    if (params.tags && params.tags.length > 0) {
      filtered = filtered.filter(p => p.tags.some(t => params.tags!.includes(t)))
    }

    const total = filtered.length
    const page = params.page || 1
    const limit = params.limit || 12
    const start = (page - 1) * limit
    const end = start + limit
    
    const products = filtered.slice(start, end)

    return {
      products,
      total,
      page,
      limit,
      pages: Math.ceil(total / limit)
    }
  },

  async getFeaturedProducts(): Promise<Product[]> {
    // 🔄 使用後端 API 或 mock 數據
    if (USE_BACKEND_API) {
      try {
        console.log('🌐 [ProductService] 使用後端 API 獲取精選產品')
        return await productApiService.getFeaturedProducts()
      } catch (error) {
        console.warn('⚠️ [ProductService] API 失敗，降級到 mock 數據:', error)
      }
    }

    console.log('📦 [ProductService] 使用 mock 精選產品')
    await new Promise(resolve => setTimeout(resolve, 300))
    return mockProducts.filter(p => p.is_featured)
  },

  async getProductById(id: string): Promise<Product | undefined> {
    // 🔄 使用後端 API 或 mock 數據
    if (USE_BACKEND_API) {
      try {
        console.log('🌐 [ProductService] 使用後端 API 獲取產品:', id)
        return await productApiService.getProductById(id)
      } catch (error) {
        console.warn('⚠️ [ProductService] API 失敗，降級到 mock 數據:', error)
      }
    }

    console.log('📦 [ProductService] 使用 mock 產品數據:', id)
    await new Promise(resolve => setTimeout(resolve, 200))
    return mockProducts.find(p => p.id === id)
  },

  async getTags(): Promise<string[]> {
    // 🔄 使用後端 API 或 mock 數據
    if (USE_BACKEND_API) {
      try {
        console.log('🌐 [ProductService] 使用後端 API 獲取標籤')
        return await productApiService.getTags()
      } catch (error) {
        console.warn('⚠️ [ProductService] API 失敗，降級到 mock 數據:', error)
      }
    }

    console.log('📦 [ProductService] 使用 mock 標籤')
    const categories = await categoryService.getCategories()
    return categories.map(c => c.name)
  }
}
