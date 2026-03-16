<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productService } from '@/services/productService'
import { categoryService } from '@/services/categoryService'
import type { Product } from '@/models/Product'
import type { Category } from '@/models/Category'
import ProductCard from '@/components/product/ProductCard.vue'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import FeaturedProducts from '@/components/home/FeaturedProducts.vue'
import PromotionBlock from '@/components/home/PromotionBlock.vue'
import SearchBar from '@/components/ui/SearchBar.vue'
import TagFilter from '@/components/product/TagFilter.vue'
import Pagination from '@/components/ui/Pagination.vue'
import { Button } from '@/components/ui/button'

const route = useRoute()
const router = useRouter()
const products = ref<Product[]>([])
const allCategories = ref<Category[]>([])
const isFiltering = ref(false)

// Filter state
const searchQuery = ref('')
const selectedTags = ref<string[]>([])

// Pagination state
const page = ref(1)
const limit = ref(12)
const total = ref(0)

const loadProducts = async () => {
  const tag = route.query.tag as string
  const viewAll = route.query.view === 'all'

  // Determine if we should be in filtering mode (List View)
  const shouldFilter = selectedTags.value.length > 0 || searchQuery.value || tag || viewAll

  if (shouldFilter) {
    isFiltering.value = true
    
    // Find category IDs from selected tags
    const categoryIds: number[] = []
    if (selectedTags.value.length > 0) {
      // Find IDs for all selected tags
      selectedTags.value.forEach(tagName => {
        const cat = allCategories.value.find(c => c.name === tagName)
        if (cat) categoryIds.push(Number(cat.id))
      })
    }

    const response = await productService.getProducts({ 
      tags: selectedTags.value,
      categoryIds: categoryIds.length > 0 ? categoryIds : undefined,
      query: searchQuery.value,
      page: page.value,
      limit: limit.value
    })
    products.value = response.products
    total.value = response.total
  } else {
    isFiltering.value = false
    selectedTags.value = []
    searchQuery.value = ''
    products.value = []
    total.value = 0
  }
}

const loadCategories = async () => {
  try {
    allCategories.value = await categoryService.getCategories()
  } catch (e) {
    console.error('Failed to load categories', e)
  }
}

const handleSearch = () => {
  isFiltering.value = true
  page.value = 1
  loadProducts()
}

const handleTagChange = (tags: string[]) => {
  selectedTags.value = tags
  page.value = 1
  isFiltering.value = true 

  if (tags.length === 1) {
    router.push({ query: { tag: tags[0] } })
  } else {
     router.push({ query: { view: 'all' } })
  }
  
  loadProducts()
}

const handlePageChange = (newPage: number) => {
  page.value = newPage
  loadProducts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(async () => {
  await loadCategories()
  
  // Set initial selected tags from URL if present
  const tag = route.query.tag as string
  if (tag) {
    selectedTags.value = [tag]
  }
  
  await loadProducts()
})

watch(() => [route.query.tag, route.query.view], async ([newTag, newView]) => {
    if (newTag && typeof newTag === 'string') {
        selectedTags.value = [newTag]
        isFiltering.value = true
        page.value = 1
        await loadProducts()
    } else if (newView === 'all') {
        if (!isFiltering.value || (selectedTags.value.length === 0 && !searchQuery.value)) {
             selectedTags.value = []
             searchQuery.value = ''
             isFiltering.value = true
             page.value = 1
             await loadProducts()
        }
    } else if (!newTag && !newView) {
        isFiltering.value = false
        selectedTags.value = []
        searchQuery.value = ''
    }
})
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Navbar />

    <main class="flex-grow">
      <template v-if="!isFiltering">
        <!-- US3: Promotion Block -->
        <PromotionBlock />
        
        <!-- US1: Featured Products -->
        <FeaturedProducts />
      </template>

      <template v-else>
        <!-- Category Filtered View -->
        <div class="container mx-auto py-12 px-4">
          <div class="mb-10 space-y-6">
             <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b pb-6">
               <h2 class="text-3xl font-bold tracking-tight">全部商品</h2>
               <div class="w-full md:w-auto">
                 <SearchBar v-model="searchQuery" @search="handleSearch" />
               </div>
             </div>
             
             <div class="space-y-2">
               <h3 class="text-sm font-medium text-muted-foreground">分類篩選</h3>
               <TagFilter 
                 :tags="allCategories.map(c => c.name)" 
                 :selectedTags="selectedTags" 
                 @update:selectedTags="handleTagChange" 
               />
             </div>
          </div>
          
          <div v-if="products.length === 0" class="flex flex-col items-center justify-center py-12 text-center bg-muted/30 rounded-lg">
             <p class="text-xl text-muted-foreground">沒有找到符合條件的商品。</p>
             <Button variant="link" @click="selectedTags = []; searchQuery = ''; loadProducts()" class="mt-2">清除篩選條件</Button>
          </div>

          <div v-else>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              <ProductCard 
                v-for="product in products" 
                :key="product.id" 
                :product="product" 
              />
            </div>
            
            <div class="mt-8 border-t pt-4">
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
    </main>

    <Footer />
  </div>
</template>
