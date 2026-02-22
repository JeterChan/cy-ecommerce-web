import { describe, it, expect } from 'vitest'
import { categoryService } from '@/services/categoryService'

describe('CategoryService', () => {
  it('should fetch category tree (list of categories)', async () => {
    const categories = await categoryService.getTree()
    expect(Array.isArray(categories)).toBe(true)
    expect(categories.length).toBeGreaterThan(0)
    expect(categories[0]).toHaveProperty('id')
    expect(categories[0]).toHaveProperty('name')
  })

  it('should get category by id', async () => {
    const categories = await categoryService.getTree()
    const firstCategory = categories[0]
    
    const fetched = await categoryService.getById(firstCategory.id)
    expect(fetched).toBeDefined()
    expect(fetched?.id).toBe(firstCategory.id)
  })

  it('should return undefined for non-existent id', async () => {
    const fetched = await categoryService.getById('non-existent-id')
    expect(fetched).toBeUndefined()
  })
})
