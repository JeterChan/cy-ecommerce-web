<script setup lang="ts">
import { type HTMLAttributes } from 'vue'
import { DialogTitle, useForwardProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<{ class?: HTMLAttributes['class'] }>()
const forwarded = useForwardProps(props)
</script>

<template>
  <DialogTitle
    :class="cn('text-lg font-semibold leading-none tracking-tight', forwarded.class)"
  >
    <slot />
  </DialogTitle>
</template>
