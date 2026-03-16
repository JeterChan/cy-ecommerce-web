<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Plus, Pencil, Trash2, Power, PowerOff, Loader2, Search, X } from 'lucide-vue-next'
import { adminProductService } from '@/services/adminProductService'
import { categoryService, type AdminCategory } from '@/services/categoryService'
import type { Product } from '@/models/Product'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import Pagination from '@/components/ui/Pagination.vue'
import ProductForm from '@/components/admin/ProductForm.vue'
import { useToast } from '@/composables/useToast'

const LIMIT = 10

const products = ref<Product[]>([])
const total = ref(0)
const currentPage = ref(1)
const isLoading = ref(true)
const isSheetOpen = ref(false)
const editingProduct = ref<Partial<Product> | null>(null)
const { showSuccess, showError } = useToast()

// Filters
const searchQuery = ref('')
const selectedCategoryId = ref<number | null>(null)
const sortOrder = ref<'created_desc' | 'created_asc'>('created_desc')
const categories = ref<AdminCategory[]>([])

// Debounce search
let searchTimer: ReturnType<typeof setTimeout>
const onSearchInput = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadProducts()
  }, 400)
}

const onFilterChange = () => {
  currentPage.value = 1
  loadProducts()
}

const clearSearch = () => {
  searchQuery.value = ''
  currentPage.value = 1
  loadProducts()
}

const openCreateSheet = () => {
  editingProduct.value = null
  isSheetOpen.value = true
}

const openEditSheet = (product: Product) => {
  editingProduct.value = {
    ...product,
    stock_quantity: product.stockQuantity,
    is_active: product.isActive,
    category_ids: product.categoryIds,
    image_urls: product.imageUrls?.length ? product.imageUrls : (product.imageUrl ? [product.imageUrl] : []),
    images: product.images
  }
  isSheetOpen.value = true
}

const handleFormSuccess = () => {
  isSheetOpen.value = false
  loadProducts()
}

const loadProducts = async () => {
  try {
    isLoading.value = true
    const response = await adminProductService.getAdminProducts({
      page: currentPage.value,
      limit: LIMIT,
      search: searchQuery.value || undefined,
      category_id: selectedCategoryId.value,
      sort: sortOrder.value,
    })
    products.value = response.products
    total.value = response.total
  } catch (error) {
    showError('無法載入商品列表')
  } finally {
    isLoading.value = false
  }
}

const toggleActive = async (product: Product) => {
  try {
    const newStatus = !product.isActive
    await adminProductService.updateProduct(product.id, { is_active: newStatus })
    product.isActive = newStatus
    showSuccess(`商品已${newStatus ? '上架' : '下架'}`)
  } catch (error) {
    showError('操作失敗')
  }
}

const handleDelete = async (id: string) => {
  try {
    await adminProductService.deleteProduct(id)
    products.value = products.value.filter(p => p.id !== id)
    total.value = Math.max(0, total.value - 1)
    showSuccess('商品已刪除')
  } catch (error) {
    showError('刪除失敗')
  }
}

onMounted(async () => {
  const [_, cats] = await Promise.allSettled([
    loadProducts(),
    categoryService.getAdminCategories()
  ])
  if (cats.status === 'fulfilled') categories.value = cats.value
})

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(price)
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">商品管理</h1>
      <Sheet v-model:open="isSheetOpen">
        <SheetTrigger as-child>
          <Button @click="openCreateSheet" class="flex items-center gap-2">
            <Plus class="w-4 h-4" /> 新增商品
          </Button>
        </SheetTrigger>
        <SheetContent side="right" class="sm:max-w-2xl overflow-y-auto">
          <SheetHeader class="mb-6">
            <SheetTitle>{{ editingProduct?.id ? '編輯商品' : '新增商品' }}</SheetTitle>
          </SheetHeader>
          <ProductForm 
            v-if="isSheetOpen"
            :initial-values="editingProduct || undefined" 
            @success="handleFormSuccess"
            @cancel="isSheetOpen = false"
          />
        </SheetContent>
      </Sheet>
    </div>

    <!-- Search & Filter Bar -->
    <div class="flex flex-wrap gap-3 mb-4">
      <!-- Search -->
      <div class="relative flex-1 min-w-[200px]">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          v-model="searchQuery"
          @input="onSearchInput"
          type="text"
          placeholder="搜尋商品名稱..."
          class="w-full pl-9 pr-8 py-2 text-sm border rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <button v-if="searchQuery" @click="clearSearch" class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Category Filter -->
      <select
        v-model="selectedCategoryId"
        @change="onFilterChange"
        class="px-3 py-2 text-sm border rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-primary"
      >
        <option :value="null">所有分類</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
      </select>

      <!-- Sort -->
      <select
        v-model="sortOrder"
        @change="onFilterChange"
        class="px-3 py-2 text-sm border rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-primary"
      >
        <option value="created_desc">上架時間：新→舊</option>
        <option value="created_asc">上架時間：舊→新</option>
      </select>
    </div>

    <!-- Table -->
    <Card>
      <CardHeader>
        <CardTitle>商品列表（共 {{ total }} 筆）</CardTitle>
      </CardHeader>
      <CardContent>
        <div v-if="isLoading" class="flex justify-center py-12">
          <Loader2 class="w-8 h-8 animate-spin text-primary" />
        </div>
        
        <div v-else-if="products.length === 0" class="py-12 text-center text-gray-400">
          找不到符合條件的商品
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
            <thead class="text-xs text-gray-700 uppercase bg-gray-100 dark:bg-gray-800 dark:text-gray-400">
              <tr>
                <th class="px-4 py-3">商品</th>
                <th class="px-4 py-3">分類</th>
                <th class="px-4 py-3">價格</th>
                <th class="px-4 py-3">庫存</th>
                <th class="px-4 py-3">狀態</th>
                <th class="px-4 py-3 text-right">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="product in products"
                :key="product.id"
                class="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <td class="px-4 py-4 flex items-center gap-3">
                  <img :src="product.imageUrl" class="w-10 h-10 rounded object-cover bg-gray-100" />
                  <span class="font-medium text-gray-900 dark:text-white">{{ product.name }}</span>
                </td>
                <td class="px-4 py-4">
                  <div class="flex flex-wrap gap-1">
                    <Badge
                      v-for="name in product.categoryNames"
                      :key="name"
                      variant="outline"
                      class="text-xs"
                    >{{ name }}</Badge>
                    <span v-if="!product.categoryNames?.length" class="text-gray-300">—</span>
                  </div>
                </td>
                <td class="px-4 py-4">{{ formatPrice(product.price) }}</td>
                <td class="px-4 py-4">
                  <span :class="{ 'text-red-500 font-bold': (product.stockQuantity || 0) < 5 }">
                    {{ product.stockQuantity }}
                  </span>
                </td>
                <td class="px-4 py-4">
                  <Badge :variant="product.isActive ? 'default' : 'secondary'">
                    {{ product.isActive ? '上架中' : '已下架' }}
                  </Badge>
                </td>
                <td class="px-4 py-4 text-right flex justify-end gap-2">
                  <Button variant="ghost" size="icon" @click="toggleActive(product)" :title="product.isActive ? '下架' : '上架'">
                    <Power v-if="!product.isActive" class="w-4 h-4" />
                    <PowerOff v-else class="w-4 h-4 text-red-500" />
                  </Button>
                  <Button variant="ghost" size="icon" @click="openEditSheet(product)">
                    <Pencil class="w-4 h-4" />
                  </Button>
                  <ConfirmDialog
                    title="確定刪除？"
                    description="刪除後將無法復原此商品。"
                    @confirm="handleDelete(product.id)"
                  >
                    <template #trigger>
                      <Button variant="ghost" size="icon" class="text-red-500">
                        <Trash2 class="w-4 h-4" />
                      </Button>
                    </template>
                  </ConfirmDialog>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <Pagination
          :page="currentPage"
          :limit="LIMIT"
          :total="total"
          @update:page="(p) => { currentPage = p; loadProducts() }"
        />
      </CardContent>
    </Card>
  </div>
</template>
