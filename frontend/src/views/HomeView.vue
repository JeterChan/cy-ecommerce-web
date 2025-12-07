<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productService } from '@/services/productService'
import type { Product } from '@/models/Product'
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
const allTags = ref<string[]>([])
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
    
    // If route has a tag and we have no local tags selected (e.g. fresh load), use it
    if (tag && selectedTags.value.length === 0) {
        selectedTags.value = [tag]
    }

    const response = await productService.getProducts({ 
      tags: selectedTags.value,
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

const loadTags = async () => {
  try {
    allTags.value = await productService.getTags()
  } catch (e) {
    console.error('Failed to load tags', e)
  }
}

const handleSearch = () => {
  // Search implies filtering mode
  isFiltering.value = true
  page.value = 1
  loadProducts()
}

const handleTagChange = (tags: string[]) => {
  selectedTags.value = tags
  page.value = 1
  
  // Interaction implies filtering mode
  isFiltering.value = true 

  // Update URL query for bookmarkability
  if (tags.length === 1) {
    router.push({ query: { tag: tags[0] } })
  } else if (tags.length === 0) {
    // If clearing tags, we likely want to see "All Products" list unless search is also empty...
    // But traditionally "All" button in filters means "Show everything".
    router.push({ query: { view: 'all' } })
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
  await loadTags()
  await loadProducts()
})

watch(() => [route.query.tag, route.query.view], async ([newTag, newView]) => {
    // If route changes to a specific tag, override selection (e.g. browser back button)
    if (newTag && typeof newTag === 'string') {
        selectedTags.value = [newTag]
        isFiltering.value = true
        page.value = 1
        await loadProducts()
    } else if (newView === 'all') {
        // If switching to "View All" via route (e.g. Navbar link), reset filters IF we weren't already manually filtering
        // Actually, Navbar "All Products" link should probably clear filters.
        // But if we just added a second tag, route goes to view=all. We DON'T want to clear filters then.
        // So we only clear if we are NOT already filtering (which is tricky) OR if we explicitly decide Navbar link clears.
        
        // Current logic: If we are entering 'all' view from 'featured', setup list.
        // If we are already in list mode (isFiltering=true), assume valid state unless...
        if (!isFiltering.value) {
             selectedTags.value = []
             searchQuery.value = ''
             isFiltering.value = true
             page.value = 1
             await loadProducts()
        }
    } else if (!newTag && !newView) {
        // Route has no params -> Default Home
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
                 :tags="allTags" 
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
