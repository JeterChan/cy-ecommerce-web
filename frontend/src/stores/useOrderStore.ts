import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Order, OrderDetail, OrderSearchParams } from '@/types/order'
import { orderService } from '@/services/orderService'

export const useOrderStore = defineStore('order', () => {
  const orders = ref<Order[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const limit = ref(4)
  const currentOrder = ref<OrderDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchOrders = async (params: OrderSearchParams = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await orderService.getOrders(params)
      orders.value = response.items
      total.value = response.total
      currentPage.value = response.page
      limit.value = response.limit
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch orders'
    } finally {
      loading.value = false
    }
  }

  const fetchOrderDetails = async (id: string) => {
    loading.value = true
    error.value = null
    currentOrder.value = null
    try {
      const order = await orderService.getOrder(id)
      currentOrder.value = order
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch order details'
    } finally {
      loading.value = false
    }
  }

  const cancelOrder = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const result = await orderService.cancelOrder(id)
      
      // Update local state if successful
      if (currentOrder.value && currentOrder.value.id === id) {
        currentOrder.value.status = result.status
      }
      
      const index = orders.value.findIndex(o => o.id === id)
      if (index !== -1 && orders.value[index]) {
        orders.value[index].status = result.status
      }
      
      return true
    } catch (err: any) {
      error.value = err.message || 'Failed to cancel order'
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    orders,
    total,
    currentPage,
    limit,
    currentOrder,
    loading,
    error,
    fetchOrders,
    fetchOrderDetails,
    cancelOrder
  }
})