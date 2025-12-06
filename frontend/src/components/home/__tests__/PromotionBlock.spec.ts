import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import PromotionBlock from '../PromotionBlock.vue';

// Mock promotionService
vi.mock('@/services/promotionService', () => ({
  promotionService: {
    getCurrentPromotion: vi.fn(() => Promise.resolve({
      title: 'Test Promo',
      description: 'Test Discount',
      threshold: 1000,
      discount_rate: 0.9
    }))
  }
}));

describe('PromotionBlock', () => {
  it('renders promotion details', async () => {
    const wrapper = mount(PromotionBlock);
    
    // Wait for async data
    await new Promise(resolve => setTimeout(resolve, 0));
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('Test Promo');
    expect(wrapper.text()).toContain('Test Discount');
  });
});
