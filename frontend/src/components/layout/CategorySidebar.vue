<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { categoryService } from '@/services/categoryService'
import type { Category } from '@/models/Category'

const props = defineProps<{
  activeCategoryId?: string
}>()

const categories = ref<Category[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    categories.value = await categoryService.getTree()
  } finally {
    loading.value = false
  }
})

// Build tree structure for rendering
const categoryTree = computed(() => {
  const roots = categories.value.filter(c => !c.parentId)
  return roots.map(root => ({
    ...root,
    children: categories.value.filter(c => c.parentId === root.id)
  }))
})

const isActive = (id: string) => {
  return props.activeCategoryId === id
}
</script>

<template>
  <nav class="w-full bg-white rounded-lg shadow p-4">
    <h3 class="font-bold text-lg mb-4 text-gray-800">商品分類</h3>
    
    <div v-if="loading" class="animate-pulse space-y-3">
      <div class="h-4 bg-gray-200 rounded w-3/4"></div>
      <div class="h-4 bg-gray-200 rounded w-1/2"></div>
      <div class="h-4 bg-gray-200 rounded w-5/6"></div>
    </div>

    <ul v-else class="space-y-1">
      <li v-for="root in categoryTree" :key="root.id" class="group">
        <!-- Root Category -->
        <router-link 
          :to="{ path: '/', query: { tag: root.name } }"
          class="block py-2 px-2 rounded font-medium truncate transition-colors"
          :class="[
            isActive(root.id) 
              ? 'bg-primary/10 text-primary font-bold' 
              : 'text-gray-700 hover:bg-gray-100'
          ]"
          :title="root.name"
        >
          {{ root.name }}
        </router-link>

        <!-- Children Categories -->
        <ul v-if="root.children.length > 0" class="ml-4 border-l-2 border-gray-100 pl-2 mt-1 space-y-1">
          <li v-for="child in root.children" :key="child.id">
            <router-link 
              :to="{ path: '/', query: { tag: child.name } }"
              class="block py-1 px-2 text-sm rounded truncate transition-colors"
              :class="[
                isActive(child.id) 
                  ? 'bg-primary/10 text-primary font-bold' 
                  : 'text-gray-600 hover:text-primary hover:bg-gray-50'
              ]"
              :title="child.name"
            >
              {{ child.name }}
            </router-link>
          </li>
        </ul>
      </li>
    </ul>
  </nav>
</template>
