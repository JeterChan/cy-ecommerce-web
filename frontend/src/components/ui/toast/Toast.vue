<script setup lang="ts">
import { ToastRoot, type ToastRootProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<ToastRootProps & { class?: string }>()
</script>

<template>
  <ToastRoot
    v-bind="props"
    :class="cn(
      'group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all data-[swipe=cancel]:translate-x-0 data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)] data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=move]:transition-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-bottom-full',
      props.class
    )"
  >
    <slot />
  </ToastRoot>
</template>

