<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Check } from 'lucide-vue-next'
import type { Product } from '@/models/Product'
import { productService } from '@/services/productService'
import { useCartStore } from '@/stores/cart'
import QuantitySelector from '@/components/ui/QuantitySelector.vue'

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

const handleAddToCart = () => {
  if (product.value) {
    cartStore.addToCart(product.value, quantity.value)
    addedSuccess.value = true
    // Reset success message after 2 seconds
    setTimeout(() => {
      addedSuccess.value = false
    }, 2000)
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
  <div class="max-w-4xl mx-auto">
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
        <div class="md:flex-shrink-0 md:w-1/2 h-64 md:h-auto bg-gray-100">
          <img class="w-full h-full object-cover" :src="product.imageUrl" :alt="product.name">
        </div>
        <div class="p-8 md:w-1/2 flex flex-col justify-center">
          <div class="flex flex-wrap gap-2 mb-4">
             <span v-for="tag in product.tags" :key="tag" class="text-xs bg-slate-100 text-slate-700 px-3 py-1 rounded-full font-medium">
               {{ tag }}
             </span>
          </div>
          <h1 class="text-3xl font-bold text-gray-900 mb-4 leading-tight">{{ product.name }}</h1>
          <div class="text-3xl font-bold text-slate-900 mb-6">{{ formatPrice(product.price) }}</div>
          <p class="text-gray-600 mb-8 leading-relaxed text-lg">{{ product.description }}</p>
          
          <div class="mt-auto pt-6 border-t border-gray-100">
            <div class="flex items-center gap-4 mb-6">
              <span class="text-gray-700 font-medium">數量</span>
              <QuantitySelector v-model="quantity" />
            </div>
            
            <button 
              @click="handleAddToCart"
              class="w-full bg-slate-900 text-white py-4 px-6 rounded-lg font-bold text-lg hover:bg-slate-800 transition-all active:scale-[0.98] shadow-lg hover:shadow-xl flex justify-center items-center gap-2"
              :class="{ 'bg-green-600 hover:bg-green-700': addedSuccess }"
            >
              <span v-if="addedSuccess" class="flex items-center gap-2 animate-in fade-in slide-in-from-bottom-1 duration-300">
                 <Check class="w-5 h-5" /> 已加入購物車
              </span>
              <span v-else>加入購物車</span>
            </button>
            <p class="text-center text-xs text-gray-400 mt-3">
              * 此為展示頁面，不提供實際結帳功能
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
