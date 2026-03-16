<script setup lang="ts">
import { ref, watch } from 'vue'
import { ShippingMethod, type ShippingInfo } from '@/types/orderInfo'

const props = defineProps<{
  modelValue: ShippingInfo
  note?: string
  errors?: Partial<Record<keyof ShippingInfo, string>>
  purchaserName?: string
  purchaserPhone?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: ShippingInfo): void
  (e: 'update:note', value: string): void
}>()

const form = ref<ShippingInfo>({ ...props.modelValue })
const orderNote = ref(props.note || '')
const sameAsPurchaser = ref(false)

// 用於暫存使用者在勾選「同訂購人」之前手動輸入的內容
const savedName = ref(form.value.recipient_name)
const savedPhone = ref(form.value.recipient_phone)

watch(form, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

watch(orderNote, (newValue) => {
  emit('update:note', newValue)
})

// 當勾選狀態改變時，處理資訊同步或還原
watch(sameAsPurchaser, (newValue) => {
  if (newValue) {
    // 勾選時：備份當前輸入，並套用訂購人資訊
    savedName.value = form.value.recipient_name
    savedPhone.value = form.value.recipient_phone
    if (props.purchaserName) form.value.recipient_name = props.purchaserName
    if (props.purchaserPhone) form.value.recipient_phone = props.purchaserPhone
  } else {
    // 取消勾選時：還原先前的輸入內容
    form.value.recipient_name = savedName.value
    form.value.recipient_phone = savedPhone.value
  }
})

// Update form when purchaser info changes IF checkbox is checked
watch(() => [props.purchaserName, props.purchaserPhone], ([newName, newPhone]) => {
  if (sameAsPurchaser.value) {
    if (newName) form.value.recipient_name = newName
    if (newPhone) form.value.recipient_phone = newPhone
  }
})
</script>

<template>
  <div class="bg-white rounded-lg border p-6 mb-6">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-lg font-bold">運送資訊</h2>
      <label for="sameAsPurchaser" class="flex items-center space-x-2 text-sm text-gray-600 cursor-pointer">
        <input 
          id="sameAsPurchaser"
          type="checkbox" 
          v-model="sameAsPurchaser"
          class="rounded border-gray-300 text-slate-900 focus:ring-slate-500"
        >
        <span>同訂購人資訊</span>
      </label>
    </div>
    
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">運送方式</label>
      <div class="flex space-x-4">
        <label class="flex items-center space-x-2 cursor-pointer">
          <input 
            type="radio" 
            v-model="form.method" 
            :value="ShippingMethod.HOME_DELIVERY"
            class="text-slate-900 focus:ring-slate-500"
            checked
          >
          <span>宅配</span>
        </label>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4">
      <div>
        <label for="recipient_name" class="block text-sm font-medium text-gray-700 mb-1">收件人姓名 <span class="text-red-500">*</span></label>
        <input 
          id="recipient_name"
          v-model="form.recipient_name"
          type="text" 
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
          :class="{ 'border-red-500': errors?.recipient_name }"
          placeholder="請輸入收件人姓名"
        />
        <p v-if="errors?.recipient_name" class="text-red-500 text-xs mt-1">{{ errors.recipient_name }}</p>
      </div>
      
      <div>
        <label for="recipient_phone" class="block text-sm font-medium text-gray-700 mb-1">收件人電話 <span class="text-red-500">*</span></label>
        <input 
          id="recipient_phone"
          v-model="form.recipient_phone"
          type="tel" 
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
          :class="{ 'border-red-500': errors?.recipient_phone }"
          placeholder="09xxxxxxxx"
        />
        <p v-if="errors?.recipient_phone" class="text-red-500 text-xs mt-1">{{ errors.recipient_phone }}</p>
      </div>
      
      <div>
        <label for="shipping_address" class="block text-sm font-medium text-gray-700 mb-1">收件地址 <span class="text-red-500">*</span></label>
        <input 
          id="shipping_address"
          v-model="form.address"
          type="text" 
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
          :class="{ 'border-red-500': errors?.address }"
          placeholder="請輸入完整地址"
        />
        <p v-if="errors?.address" class="text-red-500 text-xs mt-1">{{ errors.address }}</p>
      </div>

      <div>
        <label for="order_note" class="block text-sm font-medium text-gray-700 mb-1">訂單備註</label>
        <textarea 
          id="order_note"
          v-model="orderNote"
          rows="3"
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
          placeholder="有什麼想告訴我們的嗎？"
        ></textarea>
      </div>
    </div>
  </div>
</template>
