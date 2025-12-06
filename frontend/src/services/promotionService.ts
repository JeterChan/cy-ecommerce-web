import type { Promotion } from '@/models/Promotion';

export const promotionService = {
  async getCurrentPromotion(): Promise<Promotion> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 200));
    
    return {
      title: '滿額優惠',
      description: '消費滿 10,000 打 95 折',
      threshold: 10000,
      discount_rate: 0.95
    };
  }
};
