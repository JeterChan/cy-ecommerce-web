<script setup lang="ts">
import { ref, watch } from 'vue'
import type { PurchaserInfo } from '@/types/orderInfo'

const props = defineProps<{
  modelValue: PurchaserInfo
  errors?: Partial<Record<keyof PurchaserInfo, string>>
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: PurchaserInfo): void
}>()

const form = ref<PurchaserInfo>({ ...props.modelValue })

watch(form, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })
</script>

<template>
  <div class="bg-white rounded-lg border p-6 mb-6">
    <h2 class="text-lg font-bold mb-4">購買人資訊</h2>
    <div class="grid grid-cols-1 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">姓名 <span class="text-red-500">*</span></label>
        <input 
          v-model="form.name"
          type="text" 
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
          :class="{ 'border-red-500': errors?.name }"
          placeholder="請輸入真實姓名"
        />
        <p v-if="errors?.name" class="text-red-500 text-xs mt-1">{{ errors.name }}</p>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">電話 <span class="text-red-500">*</span></label>
        <input 
          v-model="form.phone"
          type="tel" 
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
          :class="{ 'border-red-500': errors?.phone }"
          placeholder="09xxxxxxxx"
        />
        <p v-if="errors?.phone" class="text-red-500 text-xs mt-1">{{ errors.phone }}</p>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Email <span class="text-red-500">*</span></label>
        <input 
          v-model="form.email"
          type="email" 
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
          :class="{ 'border-red-500': errors?.email }"
          placeholder="example@email.com"
        />
        <p v-if="errors?.email" class="text-red-500 text-xs mt-1">{{ errors.email }}</p>
      </div>
    </div>
  </div>
</template>
