import { createInjectionState } from '@vueuse/core'
import { ref, watch } from 'vue'
import type { EmblaCarouselType as CarouselApi, EmblaOptionsType as CarouselOptions, EmblaPluginType as CarouselPlugin } from 'embla-carousel'

export type { CarouselApi, CarouselOptions, CarouselPlugin }

export interface CarouselProps {
  opts?: CarouselOptions
  plugins?: CarouselPlugin[]
  orientation?: 'horizontal' | 'vertical'
  setApi?: (api: CarouselApi) => void
  class?: string
}

export interface CarouselEmits {
  (e: 'init-api', payload: CarouselApi): void
}

const [useProvideCarousel, useInjectCarousel] = createInjectionState(
  ({
    opts,
    orientation,
    setApi,
  }: CarouselProps, _emits: any, api: any) => {
    const carouselRef = ref<HTMLElement | null>(null)
    const canScrollPrev = ref(false)
    const canScrollNext = ref(false)

    function scrollPrev() {
      api.value?.scrollPrev()
    }

    function scrollNext() {
      api.value?.scrollNext()
    }

    function onSelect(api: CarouselApi) {
      canScrollPrev.value = api.canScrollPrev()
      canScrollNext.value = api.canScrollNext()
    }

    watch(api, (newApi) => {
      if (!newApi) return

      onSelect(newApi)
      newApi.on('reInit', onSelect)
      newApi.on('select', onSelect)

      if (setApi)
        setApi(newApi)
    }, { immediate: true })

    return {
      carouselRef,
      api,
      opts,
      orientation: orientation || 'horizontal',
      scrollPrev,
      scrollNext,
      canScrollPrev,
      canScrollNext,
    }
  },
)

function useCarousel() {
  const carouselState = useInjectCarousel()

  if (!carouselState)
    throw new Error('useCarousel must be used within a <Carousel />')

  return carouselState
}

export { useCarousel, useProvideCarousel }
