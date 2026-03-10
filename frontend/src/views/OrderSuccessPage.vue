<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import { Button } from '@/components/ui/button'

const route = useRoute()
const router = useRouter()
const orderId = route.query.orderId as string

const viewOrderDetail = () => {
  if (orderId) {
    router.push(`/orders/${orderId}`)
  } else {
    router.push('/orders')
  }
}
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Navbar />
    <main class="flex-grow container mx-auto px-4 py-16 text-center">
      <div class="mb-6">
        <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">訂購成功！</h1>
        <p class="text-gray-600">感謝您的購買，我們將盡快為您出貨。</p>
      </div>
      
      <div class="bg-gray-50 max-w-md mx-auto p-6 rounded-lg mb-8">
        <p class="text-sm text-gray-500 mb-1">訂單編號</p>
        <p class="font-mono font-medium text-lg">{{ orderId || 'Loading...' }}</p>
      </div>
      
      <div class="flex flex-col sm:flex-row justify-center gap-4">
        <Button variant="outline" @click="router.push('/')">
          繼續購物
        </Button>
        <Button @click="viewOrderDetail">
          查看訂單詳情
        </Button>
      </div>
    </main>
    <Footer />
  </div>
</template>
