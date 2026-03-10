import type { ShippingInfo, PaymentInfo, PurchaserInfo } from './orderInfo';

export const OrderStatus = {
  PENDING: 'PENDING',
  PAID: 'PAID',
  SHIPPED: 'SHIPPED',
  COMPLETED: 'COMPLETED',
  CANCELLED: 'CANCELLED'
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
  id: number;  // 後端返回的是整數，不是字串
  user_id: string;
  status: OrderStatus;
  total_amount: number;
  shipping_fee: number;
  created_at: string;
  updated_at?: string;
  items?: OrderItem[]; // 可選，列表頁面可能不需要
}

// Detailed view
export interface OrderDetail extends Order {
  items: OrderItem[];
  purchaser_info?: PurchaserInfo; // 可選，後端可能沒有此欄位
  shipping_info?: ShippingInfo; // 可選，後端可能沒有此欄位
  payment_info?: PaymentInfo; // 可選，後端可能沒有此欄位
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
