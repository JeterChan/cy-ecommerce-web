<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { Product } from '@/models/Product'

defineProps<{
  product: Product
}>()

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(price)
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 flex flex-col h-full">
    <div class="h-48 overflow-hidden bg-gray-200">
      <img :src="product.imageUrl" :alt="product.name" class="w-full h-full object-cover" loading="lazy" />
    </div>
    <div class="p-4 flex flex-col flex-grow">
      <div class="flex flex-wrap gap-1 mb-2">
        <span v-for="tag in product.tags" :key="tag" class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
          {{ tag }}
        </span>
      </div>
      <h3 class="text-lg font-semibold text-gray-900 mb-1">{{ product.name }}</h3>
      <p class="text-gray-500 text-sm mb-4 line-clamp-2 flex-grow">{{ product.description }}</p>
      <div class="flex items-center justify-between mt-auto pt-2 border-t border-gray-50">
        <span class="text-lg font-bold text-gray-900">{{ formatPrice(product.price) }}</span>
        <RouterLink :to="{ name: 'product-detail', params: { id: product.id } }" class="bg-slate-900 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-1">
          查看詳情
        </RouterLink>
      </div>
    </div>
  </div>
</template>
