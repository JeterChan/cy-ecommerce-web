<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Product } from '@/models/Product'
import { productService } from '@/services/productService'
import ProductCard from '@/components/product/ProductCard.vue'
import Pagination from '@/components/ui/Pagination.vue'
import SearchBar from '@/components/ui/SearchBar.vue'
import TagFilter from '@/components/product/TagFilter.vue'

const products = ref<Product[]>([])
const loading = ref(true)
const page = ref(1)
const limit = ref(12)
const total = ref(0)
const query = ref('')
const searchTimeout = ref<ReturnType<typeof setTimeout> | undefined>(undefined)
const tags = ref<string[]>([])
const selectedTag = ref<string | undefined>(undefined)

const fetchProducts = async () => {
  try {
    loading.value = true
    const response = await productService.getProducts({ 
      page: page.value, 
      limit: limit.value,
      query: query.value,
      tag: selectedTag.value
    })
    products.value = response.products
    total.value = response.total
  } catch (error) {
    console.error('Failed to load products', error)
  } finally {
    loading.value = false
  }
}

const fetchTags = async () => {
  try {
    tags.value = await productService.getTags()
  } catch (error) {
    console.error('Failed to load tags', error)
  }
}

onMounted(async () => {
  // Load tags first or parallel
  fetchTags()
  fetchProducts()
})

const handlePageChange = (newPage: number) => {
  page.value = newPage
  fetchProducts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleSearchInput = (newQuery: string) => {
  query.value = newQuery
  if (searchTimeout.value) clearTimeout(searchTimeout.value)
  searchTimeout.value = setTimeout(() => {
    page.value = 1
    fetchProducts()
  }, 500)
}

const handleSearchEnter = () => {
  if (searchTimeout.value) clearTimeout(searchTimeout.value)
  page.value = 1
  fetchProducts()
}

const handleTagChange = (tag: string | undefined) => {
  selectedTag.value = tag
  page.value = 1
  fetchProducts()
}
</script>

<template>
  <div>
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
      <h2 class="text-2xl font-semibold text-gray-800">最新商品</h2>
      <SearchBar 
        :model-value="query" 
        @update:model-value="handleSearchInput" 
        @search="handleSearchEnter" 
      />
    </div>
    
    <div class="mb-8">
      <TagFilter :tags="tags" :selected-tag="selectedTag" @update:selected-tag="handleTagChange" />
    </div>
    
    <div v-if="loading" class="py-12 text-center text-gray-500">
      <div class="animate-spin inline-block w-8 h-8 border-4 border-current border-t-transparent text-slate-600 rounded-full" role="status" aria-label="loading">
        <span class="sr-only">Loading...</span>
      </div>
      <p class="mt-4">商品載入中...</p>
    </div>
    
    <div v-else-if="products.length === 0" class="p-8 text-center text-gray-500 bg-white rounded-lg shadow border border-gray-100">
      <p class="text-lg font-medium">找不到相關商品</p>
      <p class="text-sm mt-2">請嘗試不同的關鍵字或清除搜尋條件</p>
    </div>
    
    <div v-else>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <ProductCard 
          v-for="product in products" 
          :key="product.id" 
          :product="product" 
        />
      </div>
      
      <div class="mt-8 border-t border-gray-100 pt-4">
        <Pagination 
          :page="page" 
          :limit="limit" 
          :total="total" 
          @update:page="handlePageChange" 
        />
      </div>
    </div>
  </div>
</template>
