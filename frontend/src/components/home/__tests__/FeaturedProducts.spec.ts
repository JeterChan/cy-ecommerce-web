import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import FeaturedProducts from '../FeaturedProducts.vue';
import { createPinia, setActivePinia } from 'pinia';
import { createRouter, createWebHistory } from 'vue-router';

// Mock productService
vi.mock('@/services/productService', () => ({
  productService: {
    getFeaturedProducts: vi.fn(() => Promise.resolve([
      { id: '1', name: 'Test Product', price: 100, imageUrl: 'img.jpg', tags: [], is_featured: true }
    ]))
  }
}));

// Setup Router Mock
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
    { path: '/product/:id', name: 'product-detail', component: { template: '<div>Detail</div>' } }
  ]
});

describe('FeaturedProducts', () => {
  it('renders section title', () => {
    setActivePinia(createPinia());
    const wrapper = mount(FeaturedProducts, {
      global: {
        plugins: [router]
      }
    });
    expect(wrapper.text()).toContain('當季精選商品');
  });

  it('renders product cards after loading', async () => {
    setActivePinia(createPinia());
    const wrapper = mount(FeaturedProducts, {
      global: {
        plugins: [router]
      }
    });
    
    // Wait for async data
    await new Promise(resolve => setTimeout(resolve, 0));
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('Test Product');
  });
});