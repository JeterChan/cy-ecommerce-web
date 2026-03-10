import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import CategorySidebar from '@/components/layout/CategorySidebar.vue'
import { categoryService } from '@/services/categoryService'

// Mock the service
vi.mock('@/services/categoryService', () => ({
  categoryService: {
    getTree: vi.fn(),
  }
}))

describe('CategorySidebar.vue', () => {
  it('renders a list of categories', async () => {
    // Mock data
    const mockCategories = [
      { id: '1', name: 'Cat 1', slug: 'cat-1', parentId: undefined },
      { id: '2', name: 'Cat 2', slug: 'cat-2', parentId: undefined }
    ]
    // @ts-ignore
    categoryService.getTree.mockResolvedValue(mockCategories)

    const wrapper = mount(CategorySidebar, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
            props: ['to']
          }
        }
      }
    })

    // Wait for async calls
    await flushPromises()

    const items = wrapper.findAll('li')
    expect(items).toHaveLength(2)
    expect(items[0].text()).toContain('Cat 1')
    expect(items[1].text()).toContain('Cat 2')
  })
})
