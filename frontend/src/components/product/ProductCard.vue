<script setup lang="ts">
import type { Product } from '@/models/Product'
import { useRouter } from 'vue-router'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

defineProps<{
  product: Product
}>()

const router = useRouter()

const goToDetail = (id: string) => {
  router.push({ name: 'product-detail', params: { id } })
}
</script>

<template>
  <Card class="overflow-hidden h-full flex flex-col hover:shadow-lg transition-shadow duration-300 cursor-pointer" @click="goToDetail(product.id)">
    <div class="relative aspect-video overflow-hidden">
      <img 
        :src="product.imageUrl" 
        :alt="product.name"
        class="object-cover w-full h-full hover:scale-105 transition-transform duration-300"
        :class="{ 'grayscale opacity-50': product.stockQuantity === 0 }"
      />
      <!-- 庫存標籤 -->
      <div class="absolute top-2 right-2 flex flex-col gap-1">
        <Badge v-if="product.stockQuantity === 0" variant="destructive" class="shadow-md">
          已售罄
        </Badge>
        <Badge v-else-if="product.isLowStock" variant="secondary" class="bg-yellow-500 hover:bg-yellow-600 text-white shadow-md">
          庫存緊張
        </Badge>
      </div>
    </div>
    
    <CardHeader class="p-4 pb-2">
      <div class="flex justify-between items-start gap-2">
        <CardTitle class="text-lg font-bold line-clamp-1" :title="product.name">
          {{ product.name }}
        </CardTitle>
        <Badge v-if="product.is_featured" variant="secondary" class="shrink-0">精選</Badge>
      </div>
    </CardHeader>

    <CardContent class="p-4 pt-0 flex-grow">
      <p class="text-sm text-muted-foreground line-clamp-2 h-10 mb-2">
        {{ product.description }}
      </p>
      <div class="flex flex-wrap gap-1">
        <Badge v-for="tag in product.tags" :key="tag" variant="outline" class="text-xs">
          {{ tag }}
        </Badge>
      </div>
    </CardContent>

    <CardFooter class="p-4 pt-0 mt-auto flex justify-between items-center">
      <span class="text-lg font-bold text-primary">
        NT$ {{ product.price.toLocaleString() }}
      </span>
      <Button variant="secondary" size="sm" @click.stop="goToDetail(product.id)">
        查看詳情
      </Button>
    </CardFooter>
  </Card>
</template>
