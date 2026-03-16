import { api } from '@/lib/api'
import type { OrderDetail, OrderListResponse, OrderSearchParams, OrderStatus } from '@/types/order'
import { ShippingMethod, PaymentStatus } from '@/types/orderInfo'

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

    // 後端返回的是 OrderListResponse 物件 { orders: [], total: ..., skip: ..., limit: ... }
    const response = await api.get<any>(BASE_URL, { params: queryParams })
    const data = response.data

    return {
      items: data.orders || [],
      total: data.total || 0,
      page: page,
      limit: limit
    }
  },

  /**
   * 取得訂單詳情
   */
  async getOrder(id: string | number): Promise<OrderDetail> {
    const response = await api.get<any>(`${BASE_URL}/${id}`)
    const data = response.data

    // 映射後端扁平資料到前端巢狀結構
    // TODO: 後端 OrderResponse 尚未包含 shipping_method，目前暫時硬編碼為 HOME_DELIVERY
    const orderDetail: OrderDetail = {
      ...data,
      shipping_info: {
        recipient_name: data.recipient_name,
        recipient_phone: data.recipient_phone,
        address: data.shipping_address,
        method: (data.shipping_method as ShippingMethod) || ShippingMethod.HOME_DELIVERY
      },
      payment_info: {
        method: data.payment_method as any,
        status: data.status === 'PENDING' ? PaymentStatus.UNPAID : PaymentStatus.PAID
      }
    }

    return orderDetail
  },

  /**
   * 取消訂單
   * 呼叫 PATCH /api/v1/orders/{id}/status 變更訂單狀態為 CANCELLED
   */
  async cancelOrder(id: number | string): Promise<{ id: string; status: OrderStatus }> {
    const response = await api.patch<any>(`${BASE_URL}/${id}/status`, {
      status: 'CANCELLED'
    })
    return {
      id: response.data.id,
      status: response.data.status
    }
  }
}
