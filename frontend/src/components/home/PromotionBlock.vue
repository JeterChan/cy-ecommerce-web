<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { promotionService } from '@/services/promotionService'
import type { Promotion } from '@/models/Promotion'
import { Skeleton } from '@/components/ui/skeleton'

const promotion = ref<Promotion | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    loading.value = true
    promotion.value = await promotionService.getCurrentPromotion()
  } catch (e) {
    console.error('Failed to load promotion:', e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <!-- 
    US3: Display promotional banner or text block explicitly stating the current discount rule 
    (e.g., "5% off on orders over 10,000").
    CHK006: Content (text, background color, size) defined? -> "Prominent style (contrast background)"
    CHK009: Above the fold visibility
  -->
  <div class="w-full bg-primary text-primary-foreground py-4 mb-8 shadow-md">
    <div class="container mx-auto px-4 text-center">
      <div v-if="loading" class="flex justify-center">
        <Skeleton class="h-6 w-64 bg-primary-foreground/20" />
      </div>
      <div v-else-if="promotion" class="animate-in fade-in slide-in-from-top-2 duration-500">
        <h3 class="text-lg md:text-xl font-bold inline-block mr-2">
          {{ promotion.title }}
        </h3>
        <span class="text-sm md:text-lg opacity-90 block md:inline">
          {{ promotion.description }}
        </span>
      </div>
    </div>
  </div>
</template>
