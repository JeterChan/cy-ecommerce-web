<script setup lang="ts">
const props = defineProps<{
  tags: string[]
  selectedTags?: string[]
}>()

const emit = defineEmits<{
  (e: 'update:selectedTags', tags: string[]): void
}>()

const selectTag = (tag: string) => {
  const currentTags = props.selectedTags || []
  if (currentTags.includes(tag)) {
    // Remove tag if already selected
    emit('update:selectedTags', currentTags.filter(t => t !== tag))
  } else {
    // Add tag to selection
    emit('update:selectedTags', [...currentTags, tag])
  }
}

const clearTags = () => {
  emit('update:selectedTags', [])
}

const isTagSelected = (tag: string) => {
  return props.selectedTags?.includes(tag) || false
}
</script>

<template>
  <div class="flex flex-wrap gap-2 py-2">
    <button
      :class="[
        'px-4 py-1.5 rounded-full text-sm font-medium transition-colors border focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-slate-500',
        (!selectedTags || selectedTags.length === 0)
          ? 'bg-slate-900 text-white border-slate-900'
          : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50 hover:border-gray-300'
      ]"
      @click="clearTags"
    >
      全部
    </button>
    <button
      v-for="tag in tags"
      :key="tag"
      :class="[
        'px-4 py-1.5 rounded-full text-sm font-medium transition-colors border focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-slate-500',
        isTagSelected(tag)
          ? 'bg-slate-900 text-white border-slate-900'
          : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50 hover:border-gray-300'
      ]"
      @click="selectTag(tag)"
    >
      {{ tag }}
    </button>
  </div>
</template>
