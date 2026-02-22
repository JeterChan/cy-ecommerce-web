<script setup lang="ts">
import { computed } from 'vue'
import { Badge } from '@/components/ui/badge'
import { OrderStatus } from '@/types/order'

const props = defineProps<{
  status: OrderStatus
}>()

const config = computed(() => {
  switch (props.status) {
    case OrderStatus.PENDING:
      return { variant: 'outline' as const, label: '待付款', customClass: 'border-yellow-500 text-yellow-700 bg-yellow-50' }
    case OrderStatus.PAID:
      return { variant: 'default' as const, label: '已付款', customClass: 'bg-blue-500 text-white' }
    case OrderStatus.SHIPPED:
      return { variant: 'secondary' as const, label: '已出貨', customClass: 'bg-purple-500 text-white' }
    case OrderStatus.COMPLETED:
      return { variant: 'secondary' as const, label: '已完成', customClass: 'bg-green-500 text-white' }
    case OrderStatus.CANCELLED:
      return { variant: 'destructive' as const, label: '已取消', customClass: '' }
    default:
      return { variant: 'outline' as const, label: props.status, customClass: '' }
  }
})
</script>

<template>
  <Badge :variant="config.variant" :class="config.customClass">
    {{ config.label }}
  </Badge>
</template>
