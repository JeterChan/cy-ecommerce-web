<script setup lang="ts">
const props = defineProps<{
  tags: string[]
  selectedTag?: string
}>()

const emit = defineEmits<{
  (e: 'update:selectedTag', tag: string | undefined): void
}>()

const selectTag = (tag: string) => {
  if (props.selectedTag === tag) {
    emit('update:selectedTag', undefined)
  } else {
    emit('update:selectedTag', tag)
  }
}
</script>

<template>
  <div class="flex flex-wrap gap-2 py-2">
    <button
      :class="[
        'px-4 py-1.5 rounded-full text-sm font-medium transition-colors border focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-slate-500',
        !selectedTag 
          ? 'bg-slate-900 text-white border-slate-900' 
          : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50 hover:border-gray-300'
      ]"
      @click="emit('update:selectedTag', undefined)"
    >
      全部
    </button>
    <button
      v-for="tag in tags"
      :key="tag"
      :class="[
        'px-4 py-1.5 rounded-full text-sm font-medium transition-colors border focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-slate-500',
        selectedTag === tag
          ? 'bg-slate-900 text-white border-slate-900'
          : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50 hover:border-gray-300'
      ]"
      @click="selectTag(tag)"
    >
      {{ tag }}
    </button>
  </div>
</template>
