<script setup lang="ts">
import { type HTMLAttributes } from 'vue'
import { DialogDescription, useForwardProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<{ class?: HTMLAttributes['class'] }>()
const forwarded = useForwardProps(props)
</script>

<template>
  <DialogDescription
    :class="cn('text-sm text-muted-foreground', forwarded.class)"
  >
    <slot />
  </DialogDescription>
</template>
