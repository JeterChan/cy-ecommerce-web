<script setup lang="ts">
import { computed } from 'vue'
import { Trash2 } from 'lucide-vue-next'
import type { CartItem } from '@/models/Cart'
import QuantitySelector from '@/components/ui/QuantitySelector.vue'

const props = defineProps<{
  item: CartItem
}>()

const emit = defineEmits<{
  (e: 'update-quantity', id: string, quantity: number): void
  (e: 'remove', id: string): void
}>()

const subtotal = computed(() => props.item.price * props.item.quantity)

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(price)
}

const onQuantityChange = (newQty: number) => {
  emit('update-quantity', props.item.productId, newQty)
}
</script>

<template>
  <div class="flex flex-col sm:flex-row items-center gap-4 py-6 border-b border-gray-100 last:border-0">
    <!-- Image -->
    <div class="w-24 h-24 flex-shrink-0 bg-gray-100 rounded-md overflow-hidden">
      <img :src="item.imageUrl" :alt="item.name" class="w-full h-full object-cover" />
    </div>
    
    <!-- Details -->
    <div class="flex-1 w-full sm:w-auto text-center sm:text-left">
      <h3 class="text-base font-medium text-gray-900">{{ item.name }}</h3>
      <p class="text-sm text-gray-500 mt-1">{{ formatPrice(item.price) }}</p>
    </div>

    <!-- Quantity -->
    <div class="flex items-center justify-center sm:justify-end w-full sm:w-auto gap-4 sm:gap-8 mt-4 sm:mt-0">
      <QuantitySelector 
        :model-value="item.quantity" 
        @update:model-value="onQuantityChange" 
      />
      
      <div class="text-right min-w-[80px]">
        <div class="font-bold text-gray-900">{{ formatPrice(subtotal) }}</div>
      </div>
      
      <button 
        @click="emit('remove', item.productId)"
        class="p-2 text-gray-400 hover:text-red-500 transition-colors rounded-full hover:bg-red-50"
        aria-label="Remove item"
      >
        <Trash2 class="w-5 h-5" />
      </button>
    </div>
  </div>
</template>
