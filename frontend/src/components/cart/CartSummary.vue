<script setup lang="ts">
defineProps<{
  totalQuantity: number
  totalAmount: number
}>()

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(price)
}
</script>

<template>
  <div class="bg-gray-50 rounded-xl p-6 h-fit sticky top-24 border border-gray-100">
    <h2 class="text-lg font-bold text-gray-900 mb-4">訂單摘要</h2>
    
    <div class="flex justify-between mb-2 text-gray-600">
      <span>共 {{ totalQuantity }} 件商品</span>
      <span>{{ formatPrice(totalAmount) }}</span>
    </div>
    
    <div class="flex justify-between mb-4 text-gray-600">
      <span>運費</span>
      <span class="text-green-600 font-medium">免運費</span>
    </div>
    
    <div class="border-t border-gray-200 pt-4 mb-6 flex justify-between items-center">
      <span class="font-bold text-gray-900 text-lg">總計</span>
      <span class="font-bold text-slate-900 text-2xl">{{ formatPrice(totalAmount) }}</span>
    </div>
    
    <button class="w-full bg-slate-900 text-white py-4 rounded-lg font-bold text-lg hover:bg-slate-800 transition-transform active:scale-[0.98] shadow-lg hover:shadow-xl">
      前往結帳
    </button>
    <p class="text-center text-xs text-gray-400 mt-3">
      * 此為展示頁面，不提供實際結帳功能
    </p>
  </div>
</template>
