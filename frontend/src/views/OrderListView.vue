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
    <main class="flex-grow container mx-auto py-6 sm:py-8 px-4 sm:px-6">
      <div class="max-w-5xl mx-auto">
        <h1 class="text-2xl sm:text-3xl font-bold mb-6 sm:mb-8">我的訂單</h1>

        <div v-if="loading && orders.length === 0" class="flex justify-center py-20">
          <Loader2 class="h-8 w-8 animate-spin text-primary" />
        </div>

        <div v-else-if="error" class="py-4">
          <Alert variant="destructive">
            <AlertTitle>錯誤</AlertTitle>
            <AlertDescription>{{ error }}</AlertDescription>
          </Alert>
        </div>

        <div v-else-if="orders.length === 0" class="text-center py-16 sm:py-20">
          <div class="bg-gray-50 rounded-xl p-8 sm:p-12 border border-dashed border-gray-300">
            <p class="text-lg text-muted-foreground mb-6">尚無訂單紀錄</p>
            <Button as-child variant="default" size="lg">
              <RouterLink to="/">開始購物</RouterLink>
            </Button>
          </div>
        </div>

        <div v-else class="space-y-8 relative">
          <div v-if="loading" class="absolute inset-0 bg-white/60 z-10 flex items-center justify-center rounded-lg backdrop-blur-[1px]">
            <Loader2 class="h-8 w-8 animate-spin text-primary" />
          </div>

          <div class="grid gap-4 sm:gap-6 grid-cols-1 md:grid-cols-2">
            <OrderCard v-for="order in orders" :key="order.id" :order="order" />
          </div>

          <div class="flex justify-center mt-10 pt-4 border-t">
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
