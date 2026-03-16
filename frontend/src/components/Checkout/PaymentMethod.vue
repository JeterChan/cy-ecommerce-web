<script setup lang="ts">
import { ref, watch } from 'vue'
import { PaymentMethod, type PaymentInfo } from '@/types/orderInfo'

const props = defineProps<{
  modelValue: PaymentInfo
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: PaymentInfo): void
}>()

const form = ref<PaymentInfo>({ ...props.modelValue })

watch(form, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })
</script>

<template>
  <div class="bg-white rounded-lg border p-6 mb-6">
    <h2 class="text-lg font-bold mb-4">付款方式</h2>
    
    <div class="grid grid-cols-1 gap-4">
      <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50" :class="{'border-slate-900 ring-1 ring-slate-900': form.method === PaymentMethod.BANK_TRANSFER}">
        <input 
          type="radio" 
          v-model="form.method" 
          :value="PaymentMethod.BANK_TRANSFER"
          class="text-slate-900 focus:ring-slate-500 mr-3"
        >
        <div>
          <p class="font-medium">銀行轉帳</p>
          <p class="text-sm text-gray-500">提供匯款帳號，請於 24 小時內付款</p>
        </div>
      </label>

      <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50" :class="{'border-slate-900 ring-1 ring-slate-900': form.method === PaymentMethod.COD}">
        <input 
          type="radio" 
          v-model="form.method" 
          :value="PaymentMethod.COD"
          class="text-slate-900 focus:ring-slate-500 mr-3"
        >
        <div>
          <p class="font-medium">貨到付款</p>
          <p class="text-sm text-gray-500">送貨上門時支付現金</p>
        </div>
      </label>
    </div>
  </div>
</template>