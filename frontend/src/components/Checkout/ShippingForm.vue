<script setup lang="ts">
import { ref, watch } from 'vue'
import { ShippingMethod, type ShippingInfo } from '@/types/orderInfo'

const props = defineProps<{
  modelValue: ShippingInfo
  note?: string
  errors?: Partial<Record<keyof ShippingInfo, string>>
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: ShippingInfo): void
  (e: 'update:note', value: string): void
}>()

const form = ref<ShippingInfo>({ ...props.modelValue })
const orderNote = ref(props.note || '')

watch(form, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

watch(orderNote, (newValue) => {
  emit('update:note', newValue)
})
</script>

<template>
  <div class="bg-white rounded-lg border p-6 mb-6">
    <h2 class="text-lg font-bold mb-4">運送資訊</h2>
    
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">運送方式</label>
      <div class="flex space-x-4">
        <label class="flex items-center space-x-2 cursor-pointer">
          <input 
            type="radio" 
            v-model="form.method" 
            :value="ShippingMethod.HOME_DELIVERY"
            class="text-slate-900 focus:ring-slate-500"
          >
          <span>宅配</span>
        </label>
        <label class="flex items-center space-x-2 cursor-pointer">
          <input 
            type="radio" 
            v-model="form.method" 
            :value="ShippingMethod.STORE_PICKUP_711"
            class="text-slate-900 focus:ring-slate-500"
          >
          <span>7-11 店到店</span>
        </label>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">收件人姓名 <span class="text-red-500">*</span></label>
        <input 
          v-model="form.recipient_name"
          type="text" 
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
          :class="{ 'border-red-500': errors?.recipient_name }"
          placeholder="請輸入收件人姓名"
        />
        <p v-if="errors?.recipient_name" class="text-red-500 text-xs mt-1">{{ errors.recipient_name }}</p>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">收件人電話 <span class="text-red-500">*</span></label>
        <input 
          v-model="form.recipient_phone"
          type="tel" 
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
          :class="{ 'border-red-500': errors?.recipient_phone }"
          placeholder="09xxxxxxxx"
        />
        <p v-if="errors?.recipient_phone" class="text-red-500 text-xs mt-1">{{ errors.recipient_phone }}</p>
      </div>
      
      <div v-if="form.method === ShippingMethod.HOME_DELIVERY">
        <label class="block text-sm font-medium text-gray-700 mb-1">收件地址 <span class="text-red-500">*</span></label>
        <input 
          v-model="form.address"
          type="text" 
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
          :class="{ 'border-red-500': errors?.address }"
          placeholder="請輸入完整地址"
        />
        <p v-if="errors?.address" class="text-red-500 text-xs mt-1">{{ errors.address }}</p>
      </div>
      
      <div v-if="form.method === ShippingMethod.STORE_PICKUP_711">
        <label class="block text-sm font-medium text-gray-700 mb-1">門市名稱/代號 <span class="text-red-500">*</span></label>
        <input 
          v-model="form.store_name"
          type="text" 
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
          :class="{ 'border-red-500': errors?.store_name }"
          placeholder="請輸入門市名稱"
        />
        <p v-if="errors?.store_name" class="text-red-500 text-xs mt-1">{{ errors.store_name }}</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">訂單備註</label>
        <textarea 
          v-model="orderNote"
          rows="3"
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
          placeholder="有什麼想告訴我們的嗎？"
        ></textarea>
      </div>
    </div>
  </div>
</template>
