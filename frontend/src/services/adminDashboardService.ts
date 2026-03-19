import { api } from '@/lib/api'

export interface DashboardStats {
  total_products: number
  low_stock_count: number
  today_orders: number
  today_sales: string
}

export const adminDashboardService = {
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await api.get<DashboardStats>('/api/v1/admin/dashboard/stats')
    return response.data
  }
}
