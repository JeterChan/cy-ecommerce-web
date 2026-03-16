<script setup lang="ts">
import { useCheckoutStore } from '@/stores/useCheckoutStore'
import { storeToRefs } from 'pinia'
import { watch } from 'vue'

const store = useCheckoutStore()
const { items, totalAmount } = storeToRefs(store)

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(price)
}

// 監控 items 的變化
watch(items, (newItems) => {
  console.log('📊 [OrderSummary] 訂單商品更新:', newItems.length, '個商品')
  console.log('📊 [OrderSummary] 商品明細:', JSON.stringify(newItems, null, 2))
}, { immediate: true, deep: true })
</script>

<template>
  <div class="bg-white rounded-lg border p-6">
    <h2 class="text-lg font-bold mb-4">訂單明細</h2>

    <!-- 空購物車提示 -->
    <div v-if="items.length === 0" class="text-center py-8 text-gray-500">
      <p class="mb-2">購物車是空的</p>
      <p class="text-sm">請先加入商品到購物車</p>
    </div>

    <!-- 商品列表 -->
    <div v-else class="space-y-4 mb-6">
      <div v-for="item in items" :key="item.id" class="flex justify-between items-center">
        <div>
          <p class="font-medium">{{ item.name }}</p>
          <p class="text-sm text-gray-500">x {{ item.quantity }}</p>
        </div>
        <p class="font-medium">{{ formatPrice(item.price * item.quantity) }}</p>
      </div>
    </div>

    <!-- 總計 -->
    <div v-if="items.length > 0" class="border-t pt-4 flex justify-between items-center font-bold text-lg">
      <span>總計</span>
      <span>{{ formatPrice(totalAmount) }}</span>
    </div>
  </div>
</template>
