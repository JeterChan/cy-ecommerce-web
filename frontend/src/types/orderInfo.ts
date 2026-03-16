export const ShippingMethod = {
  HOME_DELIVERY: 'HOME_DELIVERY',
  // STORE_PICKUP_711: 'STORE_PICKUP_711'
} as const;
export type ShippingMethod = (typeof ShippingMethod)[keyof typeof ShippingMethod];

export const PaymentMethod = {
  // CREDIT_CARD: 'CREDIT_CARD',
  COD: 'COD',
  BANK_TRANSFER: 'BANK_TRANSFER'
} as const;
export type PaymentMethod = (typeof PaymentMethod)[keyof typeof PaymentMethod];

export const PaymentStatus = {
  UNPAID: 'UNPAID',
  PAID: 'PAID',
  FAILED: 'FAILED',
  REFUNDED: 'REFUNDED'
} as const;
export type PaymentStatus = (typeof PaymentStatus)[keyof typeof PaymentStatus];

export interface ShippingInfo {
  recipient_name: string;
  recipient_phone: string;
  method: ShippingMethod;
  address?: string;
  store_id?: string;
  store_name?: string;
  tracking_number?: string;
}

export interface PurchaserInfo {
  name: string;
  phone: string;
  email: string;
}

export interface PaymentInfo {
  method: PaymentMethod;
  status: PaymentStatus;
  transaction_id?: string;
  paid_at?: string;
}
