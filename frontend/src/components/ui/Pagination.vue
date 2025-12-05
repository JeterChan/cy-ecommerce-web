<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  page: number
  limit: number
  total: number
}>()

const emit = defineEmits<{
  (e: 'update:page', page: number): void
}>()

const totalPages = computed(() => Math.ceil(props.total / props.limit))

const prevPage = () => {
  if (props.page > 1) {
    emit('update:page', props.page - 1)
  }
}

const nextPage = () => {
  if (props.page < totalPages.value) {
    emit('update:page', props.page + 1)
  }
}
</script>

<template>
  <div class="flex items-center justify-center space-x-4 py-8" v-if="totalPages > 1">
    <button 
      @click="prevPage" 
      :disabled="page === 1"
      class="px-4 py-2 rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-1"
    >
      上一頁
    </button>
    
    <span class="text-sm text-gray-600">
      第 <span class="font-medium text-gray-900">{{ page }}</span> 頁，共 <span class="font-medium text-gray-900">{{ totalPages }}</span> 頁
    </span>
    
    <button 
      @click="nextPage" 
      :disabled="page === totalPages"
      class="px-4 py-2 rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-1"
    >
      下一頁
    </button>
  </div>
</template>
