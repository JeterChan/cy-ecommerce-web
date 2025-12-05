import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { CartItem } from '../models/Cart'
import type { Product } from '../models/Product'

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])

  // Initialize from localStorage
  const storedCart = localStorage.getItem('cart')
  if (storedCart) {
    try {
      items.value = JSON.parse(storedCart)
    } catch (e) {
      console.error('Failed to parse cart from localStorage', e)
      localStorage.removeItem('cart')
    }
  }

  // Persistence
  watch(items, (newItems) => {
    localStorage.setItem('cart', JSON.stringify(newItems))
  }, { deep: true })

  // Getters
  const totalQuantity = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  const totalAmount = computed(() => {
    return items.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  })

  // Actions
  function addToCart(product: Product, quantity: number) {
    const existingItem = items.value.find(item => item.productId === product.id)
    if (existingItem) {
      existingItem.quantity += quantity
    } else {
      items.value.push({
        productId: product.id,
        name: product.name,
        price: product.price,
        imageUrl: product.imageUrl,
        quantity: quantity
      })
    }
  }

  function removeFromCart(productId: string) {
    const index = items.value.findIndex(item => item.productId === productId)
    if (index > -1) {
      items.value.splice(index, 1)
    }
  }

  function updateQuantity(productId: string, quantity: number) {
    const item = items.value.find(item => item.productId === productId)
    if (item) {
      item.quantity = quantity
      if (item.quantity <= 0) {
        removeFromCart(productId)
      }
    }
  }

  function clearCart() {
    items.value = []
  }

  return {
    items,
    totalQuantity,
    totalAmount,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart
  }
})
