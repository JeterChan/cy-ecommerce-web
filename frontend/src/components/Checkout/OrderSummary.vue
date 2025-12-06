<script setup lang="ts">
import { useCheckoutStore } from '@/stores/useCheckoutStore'
import { storeToRefs } from 'pinia'

const store = useCheckoutStore()
const { items, totalAmount } = storeToRefs(store)

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(price)
}
</script>

<template>
  <div class="bg-white rounded-lg border p-6">
    <h2 class="text-lg font-bold mb-4">訂單明細</h2>
    <div class="space-y-4 mb-6">
      <div v-for="item in items" :key="item.id" class="flex justify-between items-center">
        <div>
          <p class="font-medium">{{ item.name }}</p>
          <p class="text-sm text-gray-500">x {{ item.quantity }}</p>
        </div>
        <p class="font-medium">{{ formatPrice(item.price * item.quantity) }}</p>
      </div>
    </div>
    <div class="border-t pt-4 flex justify-between items-center font-bold text-lg">
      <span>總計</span>
      <span>{{ formatPrice(totalAmount) }}</span>
    </div>
  </div>
</template>
