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
  search_order_number?: string;
  search_recipient_name?: string;
  search_phone?: string;
  date_from?: string;
  date_to?: string;
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
    if (params.search_order_number) queryParams.append('search_order_number', params.search_order_number)
    if (params.search_recipient_name) queryParams.append('search_recipient_name', params.search_recipient_name)
    if (params.search_phone) queryParams.append('search_phone', params.search_phone)
    if (params.date_from) queryParams.append('date_from', params.date_from)
    if (params.date_to) queryParams.append('date_to', params.date_to)

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
