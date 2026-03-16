<script setup lang="ts">
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import OrderStatusBadge from './OrderStatusBadge.vue'
import type { Order } from '@/types/order'
import { useRouter } from 'vue-router'

const props = defineProps<{
  order: Order
}>()

const router = useRouter()

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(amount)
}

const navigateToDetail = () => {
  router.push(`/orders/${props.order.id}`)
}
</script>

<template>
  <Card class="cursor-pointer hover:shadow-lg transition-all duration-300 hover:border-primary/50" @click="navigateToDetail">
    <CardHeader class="pb-3">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <CardTitle class="text-base font-semibold">
          訂單編號：#{{ order.id }}
        </CardTitle>
        <OrderStatusBadge :status="order.status" />
      </div>
    </CardHeader>
    <CardContent class="space-y-3">
      <div class="flex items-center justify-between text-sm text-muted-foreground">
        <span>訂單日期</span>
        <span>{{ formatDate(order.created_at) }}</span>
      </div>
      <div class="flex items-center justify-between pt-2 border-t">
        <span class="text-sm text-muted-foreground">訂單金額</span>
        <span class="text-2xl font-bold text-primary">{{ formatCurrency(order.total_amount) }}</span>
      </div>
      <div class="flex items-center justify-between text-xs text-muted-foreground">
        <span>運費</span>
        <span>{{ formatCurrency(order.shipping_fee) }}</span>
      </div>
    </CardContent>
    <CardFooter class="pt-3 border-t">
      <div class="w-full text-center text-sm text-primary font-medium">
        查看詳情 →
      </div>
    </CardFooter>
  </Card>
</template>
