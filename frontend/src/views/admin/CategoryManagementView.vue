<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Trash2, Loader2, Tag, Pencil } from 'lucide-vue-next'
import { categoryService, type AdminCategory } from '@/services/categoryService'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { useToast } from '@/composables/useToast'

const categories = ref<AdminCategory[]>([])
const isLoading = ref(true)
const isSubmitting = ref(false)
const { showSuccess, showError } = useToast()

// New category form
const newCategory = ref({
  name: '',
  slug: ''
})

const loadCategories = async () => {
  try {
    isLoading.value = true
    categories.value = await categoryService.getAdminCategories()
  } catch (error) {
    showError('無法載入分類列表')
  } finally {
    isLoading.value = false
  }
}

const handleCreate = async () => {
  if (!newCategory.value.name || !newCategory.value.slug) {
    showError('請填寫分類名稱與 Slug')
    return
  }

  try {
    isSubmitting.value = true
    const created = await categoryService.createCategory(newCategory.value)
    categories.value.push(created)
    newCategory.value = { name: '', slug: '' }
    showSuccess('分類已新增')
  } catch (error: any) {
    showError(error.response?.data?.detail || '新增失敗')
  } finally {
    isSubmitting.value = false
  }
}

const handleDelete = async (id: number) => {
  try {
    await categoryService.deleteCategory(id)
    categories.value = categories.value.filter(c => c.id !== id)
    showSuccess('分類已刪除')
  } catch (error) {
    showError('刪除失敗，該分類可能仍有商品關聯')
  }
}

// Edit dialog
const isEditOpen = ref(false)
const isEditSubmitting = ref(false)
const editingCategory = ref<AdminCategory | null>(null)
const editForm = ref({ name: '', slug: '' })

const openEditDialog = (cat: AdminCategory) => {
  editingCategory.value = cat
  editForm.value = { name: cat.name, slug: cat.slug }
  isEditOpen.value = true
}

const handleEdit = async () => {
  if (!editingCategory.value) return
  if (!editForm.value.name || !editForm.value.slug) {
    showError('請填寫分類名稱與 Slug')
    return
  }
  try {
    isEditSubmitting.value = true
    const updated = await categoryService.updateCategory(
      editingCategory.value.id,
      { name: editForm.value.name, slug: editForm.value.slug }
    )
    const idx = categories.value.findIndex(c => c.id === updated.id)
    if (idx !== -1) categories.value[idx] = updated
    isEditOpen.value = false
    showSuccess('分類已更新')
  } catch (error: any) {
    showError(error.response?.data?.detail || '更新失敗')
  } finally {
    isEditSubmitting.value = false
  }
}

// Auto-generate slug from name (basic version)
const updateSlug = () => {
  if (!newCategory.value.slug && newCategory.value.name) {
    newCategory.value.slug = newCategory.value.name
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^\w-]/g, '')
  }
}

onMounted(loadCategories)
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">分類管理</h1>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-5 gap-6">
      <!-- Create Form -->
      <Card class="md:col-span-2 h-fit">
        <CardHeader>
          <CardTitle>新增分類</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div class="space-y-2">
              <Label for="name">分類名稱</Label>
              <Input
                id="name"
                v-model="newCategory.name"
                placeholder="例如：3C 數位"
                @blur="updateSlug"
              />
            </div>
            <div class="space-y-2">
              <Label for="slug">網址代碼 (Slug)</Label>
              <Input
                id="slug"
                v-model="newCategory.slug"
                placeholder="例如：3c-digital"
              />
              <p class="text-[11px] text-muted-foreground">用於 URL，僅限小寫字母、數字與連字號。</p>
            </div>
            <Button
              class="w-full"
              :disabled="isSubmitting"
              @click="handleCreate"
            >
              <Plus v-if="!isSubmitting" class="w-4 h-4 mr-2" />
              <Loader2 v-else class="w-4 h-4 mr-2 animate-spin" />
              新增分類
            </Button>
          </div>
        </CardContent>
      </Card>

      <!-- Category List -->
      <Card class="md:col-span-3">
        <CardHeader>
          <CardTitle>現有分類 ({{ categories.length }})</CardTitle>
        </CardHeader>
        <CardContent>
          <div v-if="isLoading" class="flex justify-center py-12">
            <Loader2 class="w-8 h-8 animate-spin text-primary" />
          </div>

          <div v-else-if="categories.length === 0" class="py-12 text-center text-gray-400">
            目前沒有任何分類
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full table-fixed text-sm text-left">
              <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-800 dark:text-gray-400">
                <tr>
                  <th class="px-3 py-2 w-1/3">名稱</th>
                  <th class="px-3 py-2 w-1/3">Slug</th>
                  <th class="px-3 py-2 w-1/3 text-right">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="cat in categories"
                  :key="cat.id"
                  class="border-b dark:border-gray-700 hover:bg-gray-50/50"
                >
                  <td class="px-3 py-2 font-medium">
                    <div class="flex items-center gap-2 truncate">
                      <Tag class="w-4 h-4 text-primary shrink-0" />
                      <span class="truncate">{{ cat.name }}</span>
                    </div>
                  </td>
                  <td class="px-3 py-2 text-muted-foreground truncate">{{ cat.slug }}</td>
                  <td class="px-3 py-2 text-right flex items-center justify-end gap-0.5">
                    <Button variant="ghost" size="icon" @click="openEditDialog(cat)">
                      <Pencil class="w-4 h-4" />
                    </Button>
                    <ConfirmDialog
                      title="確定刪除分類？"
                      description="如果此分類下還有商品，可能會導致錯誤。"
                      @confirm="handleDelete(cat.id)"
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
        </CardContent>
      </Card>
    </div>
    <Dialog v-model:open="isEditOpen">
      <DialogContent class="max-w-md">
        <DialogHeader>
          <DialogTitle>編輯分類</DialogTitle>
          <DialogDescription>修改後按儲存變更。變更 Slug 可能影響現有的分類篩選書籤。</DialogDescription>
        </DialogHeader>
        <div class="space-y-4 mt-2">
          <div class="space-y-2">
            <Label for="edit-name">分類名稱</Label>
            <Input id="edit-name" v-model="editForm.name" placeholder="例如：3C 數位" />
          </div>
          <div class="space-y-2">
            <Label for="edit-slug">網址代碼 (Slug)</Label>
            <Input id="edit-slug" v-model="editForm.slug" placeholder="例如：3c-digital" />
            <p class="text-[11px] text-muted-foreground">僅限小寫字母、數字與連字號。</p>
          </div>
          <div class="flex justify-end gap-2">
            <Button variant="outline" @click="isEditOpen = false" :disabled="isEditSubmitting">取消</Button>
            <Button @click="handleEdit" :disabled="isEditSubmitting">
              <Loader2 v-if="isEditSubmitting" class="w-4 h-4 mr-2 animate-spin" />
              儲存變更
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>
