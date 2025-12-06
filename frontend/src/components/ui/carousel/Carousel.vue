<script setup lang="ts">
import useEmblaCarousel from 'embla-carousel-vue'
import { type CarouselEmits, type CarouselProps, useProvideCarousel } from './useCarousel'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<CarouselProps>(), {
  orientation: 'horizontal',
})

const emits = defineEmits<CarouselEmits>()

const [emblaNode, emblaApi] = useEmblaCarousel({
  ...props.opts,
  axis: props.orientation === 'horizontal' ? 'x' : 'y',
}, props.plugins)

useProvideCarousel({
  opts: props.opts,
  orientation: props.orientation,
  plugins: props.plugins,
  setApi: props.setApi,
}, emits, emblaApi)
</script>

<template>
  <div
    :class="cn('relative', props.class)"
    role="region"
    aria-roledescription="carousel"
  >
    <div ref="emblaNode" class="overflow-hidden">
      <slot />
    </div>
  </div>
</template>
