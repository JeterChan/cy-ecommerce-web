export enum ShippingMethod {
  HOME_DELIVERY = 'HOME_DELIVERY',
  STORE_PICKUP_711 = 'STORE_PICKUP_711'
}

export enum PaymentMethod {
  CREDIT_CARD = 'CREDIT_CARD',
  COD = 'COD',
  ATM = 'ATM'
}

export enum PaymentStatus {
  UNPAID = 'UNPAID',
  PAID = 'PAID',
  FAILED = 'FAILED',
  REFUNDED = 'REFUNDED'
}

export interface ShippingInfo {
  recipient_name: string;
  recipient_phone: string;
  method: ShippingMethod;
  address?: string;
  store_id?: string;
  store_name?: string;
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
