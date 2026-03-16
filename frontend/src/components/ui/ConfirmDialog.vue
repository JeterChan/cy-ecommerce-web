<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  title: string
  description?: string
  confirmText?: string
  cancelText?: string
  isDestructive?: boolean
}>()

const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

const isOpen = ref(false)

const open = () => {
  isOpen.value = true
}

const close = () => {
  isOpen.value = false
  emit('cancel')
}

const confirm = () => {
  isOpen.value = false
  emit('confirm')
}

defineExpose({
  open,
  close
})
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
    <div class="bg-white rounded-lg shadow-lg max-w-sm w-full p-6 dark:bg-gray-800">
      <h3 class="text-lg font-medium mb-2">{{ title }}</h3>
      <p v-if="description" class="text-sm text-gray-500 mb-6 dark:text-gray-400">
        {{ description }}
      </p>
      
      <div class="flex justify-end space-x-3">
        <button 
          @click="close"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
        >
          {{ cancelText || '取消' }}
        </button>
        <button 
          @click="confirm"
          :class="[
            'px-4 py-2 text-sm font-medium text-white rounded-md',
            isDestructive 
              ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500' 
              : 'bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500'
          ]"
        >
          {{ confirmText || '確定' }}
        </button>
      </div>
    </div>
  </div>
</template>
