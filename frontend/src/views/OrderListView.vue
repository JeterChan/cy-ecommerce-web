<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useOrderStore } from '@/stores/useOrderStore'
import OrderCard from '@/components/order/OrderCard.vue'
import Pagination from '@/components/ui/Pagination.vue'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import { Button } from '@/components/ui/button'
import { storeToRefs } from 'pinia'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Loader2 } from 'lucide-vue-next'

const store = useOrderStore()
const { orders, total, currentPage, limit, loading, error } = storeToRefs(store)

onMounted(() => {
  store.fetchOrders({ page: currentPage.value, limit: limit.value })
})

watch(currentPage, (newPage) => {
  store.fetchOrders({ page: newPage, limit: limit.value })
})
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Navbar />
    <main class="flex-grow container mx-auto py-8 px-4">
      <div class="max-w-5xl mx-auto">
        <h1 class="text-3xl font-bold mb-8">我的訂單</h1>

        <div v-if="loading && orders.length === 0" class="flex justify-center py-20">
          <Loader2 class="h-8 w-8 animate-spin text-primary" />
        </div>

        <div v-else-if="error" class="py-4">
          <Alert variant="destructive">
            <AlertTitle>錯誤</AlertTitle>
            <AlertDescription>{{ error }}</AlertDescription>
          </Alert>
        </div>

        <div v-else-if="orders.length === 0" class="text-center py-20">
          <div class="bg-gray-50 rounded-lg p-12">
            <p class="text-lg text-muted-foreground mb-4">尚無訂單紀錄</p>
            <Button as-child variant="default">
              <RouterLink to="/">開始購物</RouterLink>
            </Button>
          </div>
        </div>

        <div v-else class="space-y-6 relative">
          <div v-if="loading" class="absolute inset-0 bg-white/50 z-10 flex items-center justify-center rounded-lg">
            <Loader2 class="h-8 w-8 animate-spin text-primary" />
          </div>

          <div class="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-2">
            <OrderCard v-for="order in orders" :key="order.id" :order="order" />
          </div>

          <div class="flex justify-center mt-8">
            <Pagination
              :total="total"
              :limit="limit"
              :page="currentPage"
              @update:page="(p) => currentPage = p"
            />
          </div>
        </div>
      </div>
    </main>
    <Footer />
  </div>
</template>
