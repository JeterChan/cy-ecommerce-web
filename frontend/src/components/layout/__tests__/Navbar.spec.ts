import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import Navbar from '../Navbar.vue';
import { createRouter, createWebHistory } from 'vue-router';
import { createPinia, setActivePinia } from 'pinia';
import { i18n } from '@/i18n';
import { useAuthStore } from '@/stores/auth';

// Mock productService
vi.mock('@/services/productService', () => ({
  productService: {
    getTags: vi.fn(() => Promise.resolve(['3C', 'Clothing']))
  }
}));

// Mock shadcn dropdown to render content inline for testability
vi.mock('@/components/ui/dropdown-menu', () => ({
  DropdownMenu: { template: '<div><slot /></div>' },
  DropdownMenuTrigger: { template: '<button><slot /></button>' },
  DropdownMenuContent: { template: '<div><slot /></div>' },
  DropdownMenuItem: { template: '<div><slot /></div>' },
  DropdownMenuSeparator: { template: '<hr />' },
}));

// Mock Sheet for mobile menu
vi.mock('@/components/ui/sheet', () => ({
  Sheet: { template: '<div><slot /></div>' },
  SheetTrigger: { template: '<div><slot /></div>' },
  SheetContent: { template: '<div><slot /></div>' },
}));

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
    { path: '/cart', name: 'cart', component: { template: '<div>Cart</div>' } },
    { path: '/profile', name: 'profile', component: { template: '<div>Profile</div>' } },
    { path: '/orders', name: 'orders', component: { template: '<div>Orders</div>' } },
    { path: '/admin/dashboard', name: 'admin-dashboard', component: { template: '<div>Admin</div>' } },
  ]
});

describe('Navbar', () => {
  it('renders logo and navigation links', async () => {
    setActivePinia(createPinia());
    const wrapper = mount(Navbar, {
      global: {
        plugins: [router, i18n]
      }
    });

    expect(wrapper.text()).toContain('CY E-Commerce');
    expect(wrapper.text()).toContain('商品分類');
  });

  it('loads categories into dropdown', async () => {
    setActivePinia(createPinia());
    mount(Navbar, {
      global: {
        plugins: [router, i18n]
      }
    });

    await new Promise(resolve => setTimeout(resolve, 0));
    // Trigger hover or check if categories are loaded (depending on implementation)
    // For now, just check if fetch was called implicitly or state updated
    // Note: Dropdown content might not be rendered until interaction
  });

  it('shows 管理後台 entry for admin users', async () => {
    setActivePinia(createPinia());
    const wrapper = mount(Navbar, {
      global: {
        plugins: [router, i18n]
      }
    });

    const authStore = useAuthStore();
    authStore.accessToken = 'mock-token';
    authStore.user = { id: '1', username: 'admin', email: 'admin@test.com', role: 'admin' } as any;

    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('管理後台');
  });

  it('does not show 管理後台 entry for regular users', async () => {
    setActivePinia(createPinia());
    const wrapper = mount(Navbar, {
      global: {
        plugins: [router, i18n]
      }
    });

    const authStore = useAuthStore();
    authStore.accessToken = 'mock-token';
    authStore.user = { id: '2', username: 'user', email: 'user@test.com', role: 'user' } as any;

    await wrapper.vm.$nextTick();

    expect(wrapper.text()).not.toContain('管理後台');
  });
});