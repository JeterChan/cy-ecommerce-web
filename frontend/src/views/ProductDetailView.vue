<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Check, X } from 'lucide-vue-next'
import type { Product } from '@/models/Product'
import { productService } from '@/services/productService'
import { useCartStore } from '@/stores/cart'
import QuantitySelector from '@/components/ui/QuantitySelector.vue'
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '@/components/ui/carousel'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import CategorySidebar from '@/components/layout/CategorySidebar.vue'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const product = ref<Product | undefined>(undefined)
const loading = ref(true)
const error = ref('')
const quantity = ref(1)
const addedSuccess = ref(false)

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(price)
}

const handleAddToCart = async () => {
  if (product.value) {
    try {
      await cartStore.addToCart(product.value, quantity.value)
      addedSuccess.value = true
      // Reset success message after 2 seconds
      setTimeout(() => {
        addedSuccess.value = false
      }, 2000)
    } catch (error) {
      console.error('加入購物車失敗:', error)
    }
  }
}

onMounted(async () => {
  const id = route.params.id as string
  if (!id) {
    error.value = '無效的商品 ID'
    loading.value = false
    return
  }
  
  try {
    loading.value = true
    const data = await productService.getProductById(id)
    if (data) {
      product.value = data
    } else {
      error.value = '找不到該商品'
    }
  } catch (err) {
    error.value = '載入商品失敗，請稍後再試'
    console.error(err)
  } finally {
    loading.value = false
  }
})

const goBack = () => {
  router.back()
}
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Navbar />

    <main class="flex-grow container mx-auto py-8 px-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <!-- Sidebar -->
        <div class="md:col-span-1 order-last md:order-first">
          <CategorySidebar :activeCategoryId="product?.categoryId" />
        </div>

        <!-- Main Content -->
        <div class="md:col-span-3">
          <button @click="goBack" class="mb-6 flex items-center text-gray-600 hover:text-gray-900 transition-colors group">
            <span class="mr-2 transform group-hover:-translate-x-1 transition-transform">&larr;</span> 返回列表
          </button>

          <div v-if="loading" class="py-12 text-center">
             <div class="animate-spin inline-block w-10 h-10 border-4 border-current border-t-transparent text-slate-600 rounded-full"></div>
             <p class="mt-4 text-gray-500">載入商品詳情...</p>
          </div>

          <div v-else-if="error" class="p-8 bg-red-50 text-red-600 rounded-lg text-center border border-red-100">
            <h3 class="text-xl font-bold mb-2">發生錯誤</h3>
            <p class="mb-6">{{ error }}</p>
            <button @click="router.push('/')" class="bg-white border border-red-200 text-red-600 px-6 py-2 rounded-md hover:bg-red-50 transition-colors font-medium">
              回首頁
            </button>
          </div>

          <div v-else-if="product" class="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100">
            <div class="md:flex">
              <div class="md:flex-shrink-0 md:w-1/2 bg-gray-100 relative group">
                <Carousel v-if="product.images && product.images.length > 0" class="w-full h-full">
                  <CarouselContent>
                    <CarouselItem v-for="image in product.images" :key="image.url">
                      <div class="aspect-square">
                        <img :src="image.url" :alt="image.alt_text || product.name" class="w-full h-full object-cover" />
                      </div>
                    </CarouselItem>
                  </CarouselContent>
                  <div v-if="product.images.length > 1">
                    <CarouselPrevious class="left-2 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <CarouselNext class="right-2 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </Carousel>
                <img v-else class="w-full h-full object-cover" :src="product.imageUrl" :alt="product.name">
              </div>
              <div class="p-8 md:w-1/2 flex flex-col">
                <div class="flex flex-wrap gap-2 mb-4">
                   <span v-for="tag in product.tags" :key="tag" class="text-xs bg-slate-100 text-slate-700 px-3 py-1 rounded-full font-medium">
                     {{ tag }}
                   </span>
                </div>
                
                <h1 class="text-3xl font-bold text-gray-900 mb-2 leading-tight">{{ product.name }}</h1>
                
                <!-- 庫存狀態 -->
                <div class="mb-4">
                  <span v-if="product.stockQuantity === 0" class="text-red-600 font-bold flex items-center gap-1">
                    <X class="w-4 h-4" /> 已售罄
                  </span>
                  <span v-else-if="product.isLowStock" class="text-orange-500 font-medium flex items-center gap-1">
                    庫存緊張 (僅剩 {{ product.stockQuantity }} 件)
                  </span>
                  <span v-else class="text-green-600 text-sm">
                    庫存充足
                  </span>
                </div>

                <div class="text-3xl font-bold text-slate-900 mb-6">{{ formatPrice(product.price) }}</div>
                <p class="text-gray-600 mb-8 leading-relaxed text-lg">{{ product.description }}</p>
                
                <div class="mt-auto pt-6 border-t border-gray-100">
                  <div class="flex items-center gap-4 mb-6">
                    <span class="text-gray-700 font-medium">數量</span>
                    <QuantitySelector 
                      v-model="quantity" 
                      :max="product.stockQuantity" 
                      :disabled="product.stockQuantity === 0"
                    />
                  </div>
                  
                  <button 
                    @click="handleAddToCart"
                    :disabled="product.stockQuantity === 0 || addedSuccess"
                    class="w-full bg-primary text-primary-foreground py-4 px-6 rounded-lg font-bold text-lg hover:bg-primary/90 transition-all active:scale-[0.98] shadow-lg hover:shadow-xl flex justify-center items-center gap-2 border border-primary disabled:bg-gray-300 disabled:border-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed disabled:shadow-none"
                    :class="{ 'bg-green-600 hover:bg-green-700': addedSuccess }"
                  >
                    <template v-if="addedSuccess">
                      <span class="flex items-center gap-2 animate-in fade-in slide-in-from-bottom-1 duration-300">
                         <Check class="w-5 h-5" /> 已加入購物車
                      </span>
                    </template>
                    <template v-else-if="product.stockQuantity === 0">
                      已售罄
                    </template>
                    <template v-else>
                      加入購物車
                    </template>
                  </button>
                  <p class="text-center text-xs text-gray-400 mt-3">
                    * 此為展示頁面，不提供實際結帳功能
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>
