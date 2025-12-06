<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { productService } from '@/services/productService'
import type { Product } from '@/models/Product'
import ProductCard from '@/components/product/ProductCard.vue'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import { AlertCircle, ArrowRight } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '@/components/ui/carousel'
import Autoplay from 'embla-carousel-autoplay'

const router = useRouter()
const products = ref<Product[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    loading.value = true
    error.value = null
    products.value = await productService.getFeaturedProducts()
  } catch (e) {
    console.error('Failed to load featured products:', e)
    error.value = '無法載入精選商品，請稍後再試。'
  } finally {
    loading.value = false
  }
})

const navigateToAllProducts = () => {
  router.push({ name: 'home', query: { view: 'all' } })
}
</script>

<template>
  <section class="container mx-auto py-12 px-4">
    <div class="flex justify-between items-center mb-8">
      <h2 class="text-3xl font-bold">當季精選商品</h2>
      <Button variant="link" @click="navigateToAllProducts" class="text-muted-foreground hover:text-primary">
        查看全部商品 <ArrowRight class="ml-2 h-4 w-4" />
      </Button>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <div v-for="n in 4" :key="n" class="flex flex-col space-y-3">
        <Skeleton class="h-[200px] w-full rounded-xl" />
        <div class="space-y-2">
          <Skeleton class="h-4 w-[250px]" />
          <Skeleton class="h-4 w-[200px]" />
        </div>
      </div>
    </div>

    <!-- Error State -->
    <Alert v-else-if="error" variant="destructive" class="max-w-2xl mx-auto mb-8">
      <AlertCircle class="h-4 w-4" />
      <AlertTitle>錯誤</AlertTitle>
      <AlertDescription>{{ error }}</AlertDescription>
    </Alert>

    <!-- Empty State -->
    <div v-else-if="products.length === 0" class="text-center py-12 bg-muted/30 rounded-lg">
      <p class="text-xl text-muted-foreground">目前沒有當季精選商品，敬請期待！</p>
    </div>

    <!-- Carousel Data State -->
    <div v-else class="px-8">
      <Carousel
        class="w-full"
        :plugins="[Autoplay({ delay: 4000 })]"
        :opts="{
          align: 'start',
          loop: true,
        }"
      >
        <CarouselContent class="-ml-2 md:-ml-4">
          <CarouselItem 
            v-for="product in products" 
            :key="product.id" 
            class="pl-2 md:pl-4 md:basis-1/2 lg:basis-1/3 xl:basis-1/4"
          >
            <div class="p-1 h-full">
              <ProductCard :product="product" class="h-full" />
            </div>
          </CarouselItem>
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    </div>
  </section>
</template>