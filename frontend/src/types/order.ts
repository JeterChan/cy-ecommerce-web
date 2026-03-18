import type { ShippingInfo, PaymentInfo, PurchaserInfo } from './orderInfo';

export const OrderStatus = {
  PENDING: 'PENDING',
  PAID: 'PAID',
  SHIPPED: 'SHIPPED',
  DELIVERED: 'DELIVERED',
  COMPLETED: 'COMPLETED',
  CANCELLED: 'CANCELLED',
  REFUNDING: 'REFUNDING',
  REFUNDED: 'REFUNDED'
} as const;

export type OrderStatus = (typeof OrderStatus)[keyof typeof OrderStatus];

export interface OrderItem {
  id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
  options?: Record<string, any>;
}

// Summary view for lists
export interface Order {
  id: string;  // 後端返回的是 UUID 字串
  order_number: string; // 易讀的純數字編號
  user_id: string;
  status: OrderStatus;
  total_amount: number;
  shipping_fee?: number;
  created_at: string;
  updated_at?: string;
  status_updated_at?: string;
  items?: OrderItem[]; // 可選，列表頁面可能不需要
  admin_note?: string; // 管理員內部備註
}

// Detailed view
export interface OrderDetail extends Order {
  items: OrderItem[];
  // 支援後端扁平化欄位
  recipient_name?: string;
  recipient_phone?: string;
  shipping_address?: string;
  payment_method?: string;
  
  // 保持相容原本組件預期的巢狀結構
  purchaser_info?: PurchaserInfo; 
  shipping_info?: ShippingInfo; 
  payment_info?: PaymentInfo; 
  note?: string;
}

export interface OrderListResponse {
  items: Order[];
  total: number;
  page: number;
  limit: number;
}

export interface OrderSearchParams {
  page?: number;
  limit?: number;
  status?: OrderStatus;
}
