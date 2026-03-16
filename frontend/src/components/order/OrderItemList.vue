<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { OrderItem } from '@/types/order'

defineProps<{
  items: OrderItem[]
}>()

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(amount)
}
</script>

<template>
  <div class="border rounded-md overflow-hidden">
    <!-- 桌面版表頭 -->
    <div class="hidden md:grid bg-gray-50 px-4 py-2 border-b grid-cols-12 gap-4 text-sm font-medium text-gray-500">
      <div class="col-span-6">商品名稱</div>
      <div class="col-span-2 text-right">單價</div>
      <div class="col-span-2 text-right">數量</div>
      <div class="col-span-2 text-right">小計</div>
    </div>
    <div class="divide-y">
      <div v-for="item in items" :key="item.id" class="px-4 py-3">
        <!-- 桌面版布局 -->
        <div class="hidden md:grid grid-cols-12 gap-4 items-center">
          <div class="col-span-6">
            <RouterLink 
              :to="`/product/${item.product_id}`"
              class="font-medium text-gray-900 hover:text-primary hover:underline transition-colors"
            >
              {{ item.product_name }}
            </RouterLink>
            <div v-if="item.options" class="text-xs text-gray-500 mt-1">
              <span v-for="(value, key) in item.options" :key="key" class="mr-2">
                {{ key }}: {{ value }}
              </span>
            </div>
          </div>
          <div class="col-span-2 text-right text-sm text-gray-600">
            {{ formatCurrency(item.unit_price) }}
          </div>
          <div class="col-span-2 text-right text-sm text-gray-600">
            {{ item.quantity }}
          </div>
          <div class="col-span-2 text-right font-medium text-gray-900">
            {{ formatCurrency(item.subtotal) }}
          </div>
        </div>

        <!-- 移動版布局 -->
        <div class="md:hidden space-y-2">
          <RouterLink 
            :to="`/product/${item.product_id}`"
            class="font-medium text-gray-900 block hover:text-primary transition-colors"
          >
            {{ item.product_name }}
          </RouterLink>
          <div v-if="item.options" class="text-xs text-gray-500">
            <span v-for="(value, key) in item.options" :key="key" class="mr-2">
              {{ key }}: {{ value }}
            </span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">單價</span>
            <span class="text-gray-600">{{ formatCurrency(item.unit_price) }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">數量</span>
            <span class="text-gray-600">{{ item.quantity }}</span>
          </div>
          <div class="flex justify-between pt-2 border-t">
            <span class="text-sm font-medium">小計</span>
            <span class="font-medium text-gray-900">{{ formatCurrency(item.subtotal) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>