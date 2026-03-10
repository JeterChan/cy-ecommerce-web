<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useOrderStore } from '@/stores/useOrderStore'
import { storeToRefs } from 'pinia'
import OrderItemList from '@/components/order/OrderItemList.vue'
import OrderStatusBadge from '@/components/order/OrderStatusBadge.vue'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import { Loader2, ArrowLeft } from 'lucide-vue-next'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { OrderStatus } from '@/types/order'

const route = useRoute()
const router = useRouter()
const store = useOrderStore()
const { currentOrder, loading, error } = storeToRefs(store)

const orderId = route.params.id as string

onMounted(() => {
  store.fetchOrderDetails(orderId)
})

const handleCancelOrder = async () => {
  if (!confirm('確定要取消這筆訂單嗎？取消後無法復原。')) return
  
  await store.cancelOrder(orderId)
}

const goBack = () => {
  router.push('/orders')
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(amount)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Navbar />
    <main class="flex-grow container mx-auto py-8 px-4 max-w-4xl">
      <!-- 返回按鈕 -->
      <div class="mb-6">
        <Button variant="ghost" @click="goBack" class="gap-2">
          <ArrowLeft class="h-4 w-4" />
          返回訂單列表
        </Button>
      </div>

      <div v-if="loading && !currentOrder" class="flex justify-center py-20">
        <Loader2 class="h-8 w-8 animate-spin text-primary" />
      </div>

      <div v-else-if="error" class="py-4">
        <Alert variant="destructive">
          <AlertTitle>錯誤</AlertTitle>
          <AlertDescription>{{ error }}</AlertDescription>
        </Alert>
      </div>

      <div v-else-if="currentOrder" class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <!-- Header -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b pb-6">
          <div>
            <h1 class="text-3xl font-bold tracking-tight">訂單詳情</h1>
            <p class="text-muted-foreground mt-1 text-sm">訂單編號：{{ currentOrder.id }}</p>
          </div>
          <OrderStatusBadge :status="currentOrder.status" class="text-base px-3 py-1" />
        </div>

        <!-- Items -->
        <section>
          <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
            <span class="w-1 h-6 bg-primary rounded-full"></span>
            購買商品
          </h2>
          <OrderItemList :items="currentOrder.items" />
        </section>

        <!-- Details Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <!-- Shipping Info -->
          <section class="space-y-4 bg-white p-6 rounded-lg border shadow-sm">
            <h2 class="text-lg font-semibold border-b pb-3 mb-3">配送資訊</h2>
            <div v-if="currentOrder.shipping_info" class="space-y-3 text-sm">
              <div class="flex justify-between">
                <span class="text-muted-foreground">收件人</span>
                <span class="font-medium text-gray-900">{{ currentOrder.shipping_info.recipient_name }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">電話</span>
                <span class="font-medium text-gray-900">{{ currentOrder.shipping_info.recipient_phone }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">配送方式</span>
                <span class="font-medium text-gray-900">{{ currentOrder.shipping_info.method }}</span>
              </div>
              <div v-if="currentOrder.shipping_info.address" class="flex justify-between items-start gap-4">
                <span class="text-muted-foreground shrink-0">地址</span>
                <span class="font-medium text-right text-gray-900 break-words">{{ currentOrder.shipping_info.address }}</span>
              </div>
              <div v-if="currentOrder.shipping_info.store_name" class="flex justify-between">
                <span class="text-muted-foreground">門市</span>
                <span class="font-medium text-gray-900">{{ currentOrder.shipping_info.store_name }}</span>
              </div>
               <div v-if="currentOrder.shipping_info.tracking_number" class="flex justify-between">
                <span class="text-muted-foreground">追蹤號碼</span>
                <span class="font-medium text-gray-900">{{ currentOrder.shipping_info.tracking_number }}</span>
              </div>
            </div>
            <div v-else class="text-sm text-muted-foreground italic">
              配送資訊尚未提供
            </div>
          </section>

          <!-- Payment Info -->
          <section class="space-y-4 bg-white p-6 rounded-lg border shadow-sm">
            <h2 class="text-lg font-semibold border-b pb-3 mb-3">付款資訊</h2>
            <div v-if="currentOrder.payment_info" class="space-y-3 text-sm">
               <div class="flex justify-between">
                <span class="text-muted-foreground">付款方式</span>
                <span class="font-medium text-gray-900">{{ currentOrder.payment_info.method }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">付款狀態</span>
                <span class="font-medium text-gray-900">{{ currentOrder.payment_info.status }}</span>
              </div>
               <div class="flex justify-between">
                <span class="text-muted-foreground">訂單日期</span>
                <span class="font-medium text-gray-900">{{ formatDate(currentOrder.created_at) }}</span>
              </div>
            </div>
            <div v-else class="space-y-3 text-sm">
              <div class="flex justify-between">
                <span class="text-muted-foreground">訂單日期</span>
                <span class="font-medium text-gray-900">{{ formatDate(currentOrder.created_at) }}</span>
              </div>
              <div class="text-sm text-muted-foreground italic mt-2">
                付款資訊尚未提供
              </div>
            </div>
          </section>
        </div>

        <!-- Summary -->
        <section class="bg-gray-50 p-6 rounded-lg border space-y-3">
          <div class="flex justify-between text-sm">
            <span class="text-muted-foreground">商品小計</span>
            <span class="font-medium">{{ formatCurrency(currentOrder.total_amount - currentOrder.shipping_fee) }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted-foreground">運費</span>
            <span class="font-medium">{{ formatCurrency(currentOrder.shipping_fee) }}</span>
          </div>
          <div class="border-t border-gray-200 pt-3 mt-3 flex justify-between items-center">
            <span class="font-semibold text-lg text-gray-900">總計</span>
            <span class="font-bold text-2xl text-primary">{{ formatCurrency(currentOrder.total_amount) }}</span>
          </div>
        </section>

        <!-- Actions -->
        <div class="flex justify-end pt-4 border-t" v-if="currentOrder.status === OrderStatus.PENDING">
          <Button variant="destructive" @click="handleCancelOrder" :disabled="loading">
            取消訂單
          </Button>
        </div>
      </div>
    </main>
    <Footer />
  </div>
</template>