import { api } from '@/lib/api'
import type { OrderDetail, OrderListResponse, OrderSearchParams, OrderStatus } from '@/types/order'

const BASE_URL = '/api/v1/orders'

export const orderService = {
  /**
   * 取得訂單列表
   */
  async getOrders(params: OrderSearchParams = {}): Promise<OrderListResponse> {

    const { page = 1, limit = 10, status } = params
    const skip = (page - 1) * limit

    const queryParams: any = { skip, limit }
    if (status) {
      queryParams.status = status
    }

    const response = await api.get<OrderListResponse>(BASE_URL, { params: queryParams })

    // 轉換後端回應格式以匹配前端預期
    const backendData = response.data as any
    return {
      items: backendData.orders || [],
      total: backendData.total || 0,
      page: page,
      limit: limit
    }
  },

  /**
   * 取得訂單詳情
   */
  async getOrder(id: number | string): Promise<OrderDetail> {
    const response = await api.get<OrderDetail>(`${BASE_URL}/${id}`)
    return response.data
  },

  /**
   * 取消訂單
   */
  async cancelOrder(id: number | string): Promise<{ id: number; status: OrderStatus }> {
    // 使用 PATCH 更新訂單狀態為 CANCELLED
    const response = await api.patch<{ id: number; status: OrderStatus }>(`${BASE_URL}/${id}/status`, {
      status: 'CANCELLED'
    })
    return {
      id: response.data.id,
      status: response.data.status
    }
  }
}
