<script setup lang="ts">
import { type HTMLAttributes } from 'vue'
import { useCarousel } from './useCarousel'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()

const { carouselRef, orientation } = useCarousel()
</script>

<template>
  <div
    ref="carouselRef"
    :class="
      cn(
        'flex',
        orientation === 'horizontal' ? '-ml-4' : '-mt-4 flex-col',
        props.class,
      )
    "
  >
    <slot />
  </div>
</template>
