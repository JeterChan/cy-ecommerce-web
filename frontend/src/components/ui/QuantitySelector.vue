<script setup lang="ts">
import { Minus, Plus } from 'lucide-vue-next'
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: number
  min?: number
  max?: number
}>(), {
  min: 1,
  max: 99
})

const emit = defineEmits(['update:modelValue'])

const canDecrease = computed(() => props.modelValue > props.min)
const canIncrease = computed(() => props.modelValue < props.max)

function decrease() {
  if (canDecrease.value) {
    emit('update:modelValue', props.modelValue - 1)
  }
}

function increase() {
  if (canIncrease.value) {
    emit('update:modelValue', props.modelValue + 1)
  }
}

function handleInput(event: Event) {
  const target = event.target as HTMLInputElement
  const value = parseInt(target.value)
  
  if (isNaN(value)) {
    emit('update:modelValue', props.min)
    target.value = props.min.toString()
    return
  }
  
  if (value < props.min) {
    emit('update:modelValue', props.min)
    target.value = props.min.toString()
  } else if (value > props.max) {
    emit('update:modelValue', props.max)
    target.value = props.max.toString()
  } else {
    emit('update:modelValue', value)
  }
}
</script>

<template>
  <div class="flex items-center border border-gray-300 rounded-md w-fit bg-white">
    <button 
      type="button"
      class="p-2 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-gray-600"
      :disabled="!canDecrease"
      @click="decrease"
      aria-label="Decrease quantity"
    >
      <Minus class="w-4 h-4" />
    </button>
    <input 
      type="number" 
      class="w-12 text-center border-x border-gray-300 py-1 focus:outline-none appearance-none m-0 text-gray-900"
      :value="modelValue"
      @change="handleInput"
      :min="min"
      :max="max"
    />
    <button 
      type="button"
      class="p-2 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-gray-600"
      :disabled="!canIncrease"
      @click="increase"
      aria-label="Increase quantity"
    >
      <Plus class="w-4 h-4" />
    </button>
  </div>
</template>

<style scoped>
/* Remove spin buttons from number input */
input[type=number]::-webkit-inner-spin-button, 
input[type=number]::-webkit-outer-spin-button { 
  -webkit-appearance: none; 
  margin: 0; 
}
</style>
