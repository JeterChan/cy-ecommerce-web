/**
 * Admin Order Service
 * 
 * 管理員專用的訂單管理服務
 */
import { api } from '@/lib/api'
import type { Order, OrderDetail } from '@/types/order'

export interface AdminOrderListResponse {
  orders: Order[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface AdminOrderSearchParams {
  page?: number;
  limit?: number;
  status?: string;
}

export const adminOrderService = {
  /**
   * 獲取所有訂單列表 (分頁/篩選)
   */
  async getOrders(params: AdminOrderSearchParams = {}): Promise<AdminOrderListResponse> {
    const queryParams = new URLSearchParams()
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.limit) queryParams.append('limit', params.limit.toString())
    if (params.status) queryParams.append('status', params.status)

    const url = `/api/v1/admin/orders?${queryParams.toString()}`
    const response = await api.get<AdminOrderListResponse>(url)
    return response.data
  },

  /**
   * 獲取特定訂單詳情
   */
  async getOrderDetail(orderId: string): Promise<OrderDetail> {
    const response = await api.get<OrderDetail>(`/api/v1/admin/orders/${orderId}`)
    return response.data
  },

  /**
   * 更新訂單狀態或備註
   */
  async updateOrder(orderId: string, data: { status?: string; admin_note?: string }): Promise<OrderDetail> {
    const response = await api.patch<OrderDetail>(`/api/v1/admin/orders/${orderId}`, data)
    return response.data
  }
}
