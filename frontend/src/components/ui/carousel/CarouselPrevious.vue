<script setup lang="ts">
import { type HTMLAttributes } from 'vue'
import { ArrowLeft } from 'lucide-vue-next'
import { useCarousel } from './useCarousel'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()

const { orientation, canScrollPrev, scrollPrev } = useCarousel()
</script>

<template>
  <Button
    :disabled="!canScrollPrev"
    :class="
      cn(
        'absolute h-8 w-8 rounded-full',
        orientation === 'horizontal'
          ? '-left-12 top-1/2 -translate-y-1/2'
          : '-top-12 left-1/2 -translate-x-1/2 rotate-90',
        props.class,
      )
    "
    variant="outline"
    size="icon"
    @click="scrollPrev"
  >
    <slot>
      <ArrowLeft class="h-4 w-4" />
      <span class="sr-only">Previous slide</span>
    </slot>
  </Button>
</template>
