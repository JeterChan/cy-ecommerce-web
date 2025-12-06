import { type Order, OrderStatus } from '@/types/order';
import type  { PurchaserInfo, ShippingInfo, PaymentInfo, PaymentStatus } from '@/types/orderInfo';

// Simple UUID generator for mock service compatibility
const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

export const createOrder = async (
  items: any[],
  purchaser: PurchaserInfo,
  shipping: ShippingInfo,
  payment: PaymentInfo,
  note?: string
): Promise<Order> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const mockOrder: Order = {
        id: generateUUID(),
        user_id: 'guest_user',
        status: OrderStatus.PENDING,
        total_amount: items.reduce((sum, item) => sum + item.price * item.quantity, 0),
        shipping_fee: 60, // Default mock fee
        note: note,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        items: items.map(item => ({
          id: generateUUID(),
          product_id: item.id,
          product_name: item.name,
          quantity: item.quantity,
          unit_price: item.price,
          subtotal: item.price * item.quantity
        }))
      };
      resolve(mockOrder);
    }, 1500); // Simulate 1.5s network delay
  });
};
