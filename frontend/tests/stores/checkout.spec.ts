import { setActivePinia, createPinia } from 'pinia'
import { useCheckoutStore } from '../../src/stores/useCheckoutStore'
import { describe, it, expect, beforeEach } from 'vitest'
import { ShippingMethod } from '../../src/types/orderInfo'


describe('Checkout Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with default values', () => {
    const store = useCheckoutStore()
    expect(store.items).toEqual([])
    expect(store.totalAmount).toBe(0)
    expect(store.purchaser.name).toBe('')
    expect(store.shipping.method).toBe(ShippingMethod.HOME_DELIVERY)
  })

  it('calculates total amount correctly', () => {
    const store = useCheckoutStore()
    store.setItems([
      { price: 100, quantity: 2 },
      { price: 50, quantity: 1 }
    ])
    expect(store.totalAmount).toBe(250)
  })

  it('updates purchaser info', () => {
    const store = useCheckoutStore()
    store.purchaser.name = 'Test User'
    expect(store.purchaser.name).toBe('Test User')
  })

  it('clears items after successful submission', async () => {
    const store = useCheckoutStore()
    store.setItems([{ price: 100, quantity: 1 }])
    
    await store.submitOrder()
    
    expect(store.items.length).toBe(0)
    expect(store.isSubmitting).toBe(false)
    expect(store.error).toBe('')
  })
})
