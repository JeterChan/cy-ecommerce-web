<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { ProductSchema, type ProductFormValues } from '@/models/product.schema'
import { adminProductService } from '@/services/adminProductService'
import { categoryService, type AdminCategory } from '@/services/categoryService'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { X, Upload, CheckCircle2, Loader2, Star } from 'lucide-vue-next'
import axios from 'axios'
import { useToast } from '@/composables/useToast'

interface Props {
  initialValues?: Partial<ProductFormValues> & { id?: string }
}

const props = defineProps<Props>()
const emit = defineEmits(['success', 'cancel'])
const { showSuccess, showError } = useToast()

const isSubmitting = ref(false)
const isUploading = ref(false)
const categories = ref<AdminCategory[]>([])
const selectedCategoryIds = ref<number[]>(props.initialValues?.category_ids || [])

const uploadedImages = ref<{ url: string; is_primary: boolean; file?: File }[]>(
  props.initialValues?.images?.map(img => ({
    url: img.url,
    is_primary: img.is_primary
  })) || 
  props.initialValues?.image_urls?.map((url, index) => ({ 
    url, 
    is_primary: index === 0 
  })) || []
)

const formSchema = toTypedSchema(ProductSchema)
const { handleSubmit, errors, setFieldValue } = useForm<ProductFormValues>({
  validationSchema: formSchema,
  initialValues: props.initialValues || {
    name: '',
    price: 0,
    stock_quantity: 0,
    is_active: true,
    image_urls: []
  }
})

const { value: name } = useField<string>('name')
const { value: description } = useField<string>('description')
const { value: price } = useField<number>('price')
const { value: stockQuantity } = useField<number>('stock_quantity')

const toggleCategory = (id: number) => {
  const idx = selectedCategoryIds.value.indexOf(id)
  if (idx === -1) {
    selectedCategoryIds.value.push(id)
  } else {
    selectedCategoryIds.value.splice(idx, 1)
  }
}

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files?.length) return

  const files = Array.from(target.files)
  if (uploadedImages.value.length + files.length > 5) {
    showError('每個商品最多只能上傳 5 張圖片')
    return
  }

  isUploading.value = true
  try {
    for (const file of files) {
      const { upload_url, image_url } = await adminProductService.getPresignedUrl(file.name, file.type)
      
      await axios.put(upload_url, file, {
        headers: { 'Content-Type': file.type }
      })

      uploadedImages.value.push({
        url: image_url,
        is_primary: uploadedImages.value.length === 0
      })
    }
    updateImageUrls()
  } catch (error) {
    showError('圖片上傳失敗')
  } finally {
    isUploading.value = false
    target.value = ''
  }
}

const removeImage = (index: number) => {
  const wasPrimary = uploadedImages.value[index].is_primary
  uploadedImages.value.splice(index, 1)
  
  if (wasPrimary && uploadedImages.value.length > 0) {
    uploadedImages.value[0].is_primary = true
  }
  updateImageUrls()
}

const setPrimary = (index: number) => {
  uploadedImages.value.forEach((img, i) => {
    img.is_primary = i === index
  })
  updateImageUrls()
}

const updateImageUrls = () => {
  setFieldValue('image_urls', uploadedImages.value.map(img => img.url))
}

const onSubmit = handleSubmit(async (values) => {
  if (uploadedImages.value.length === 0) {
    showError('請至少上傳一張商品圖片')
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      ...values,
      category_ids: selectedCategoryIds.value,
      images: uploadedImages.value.map(img => ({
        url: img.url,
        is_primary: img.is_primary
      }))
    }

    if (props.initialValues?.id) {
      await adminProductService.updateProduct(props.initialValues.id, payload)
      showSuccess('商品更新成功')
    } else {
      await adminProductService.createProduct(payload)
      showSuccess('商品建立成功')
    }
    emit('success')
  } catch (error: any) {
    showError(error.message || '儲存失敗')
  } finally {
    isSubmitting.value = false
  }
})

onMounted(async () => {
  try {
    categories.value = await categoryService.getAdminCategories()
  } catch {
    // non-critical
  }
})
</script>

<template>
  <form @submit="onSubmit" class="space-y-6 bg-white dark:bg-gray-800 p-6 rounded-lg border shadow-sm">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- 基本資訊 -->
      <div class="space-y-4">
        <div>
          <Label for="name">商品名稱 *</Label>
          <Input id="name" v-model="name" placeholder="例如：質感手沖壺" :class="{ 'border-red-500': errors.name }" />
          <p v-if="errors.name" class="text-xs text-red-500 mt-1">{{ errors.name }}</p>
        </div>

        <div>
          <Label for="price">價格 (TWD) *</Label>
          <Input id="price" v-model.number="price" type="number" min="0" />
          <p v-if="errors.price" class="text-xs text-red-500 mt-1">{{ errors.price }}</p>
        </div>

        <div>
          <Label for="stock">庫存數量 *</Label>
          <Input id="stock" v-model.number="stockQuantity" type="number" min="0" />
          <p v-if="errors.stock_quantity" class="text-xs text-red-500 mt-1">{{ errors.stock_quantity }}</p>
        </div>

        <!-- 分類多選 -->
        <div>
          <Label>商品分類</Label>
          <div class="mt-2 flex flex-wrap gap-2">
            <button
              v-for="cat in categories"
              :key="cat.id"
              type="button"
              @click="toggleCategory(cat.id)"
              :class="[
                'px-3 py-1 rounded-full text-sm border transition-colors',
                selectedCategoryIds.includes(cat.id)
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 border-gray-300 dark:border-gray-600 hover:border-primary'
              ]"
            >
              {{ cat.name }}
            </button>
            <span v-if="categories.length === 0" class="text-xs text-gray-400">載入中...</span>
          </div>
          <p class="text-[11px] text-gray-500 mt-1">可選擇多個分類</p>
        </div>

        <div>
          <Label for="description">商品描述</Label>
          <textarea
            id="description"
            v-model="description"
            rows="4"
            class="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            placeholder="輸入商品詳細介紹..."
          ></textarea>
        </div>
      </div>

      <!-- 圖片管理 -->
      <div class="space-y-4">
        <Label>商品圖片 (最多 5 張，星號標記為主圖)</Label>
        
        <div class="grid grid-cols-3 gap-3">
          <div v-for="(img, index) in uploadedImages" :key="index" class="relative group aspect-square rounded-md overflow-hidden border bg-gray-50">
            <img :src="img.url" class="w-full h-full object-cover" />
            
            <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
              <button type="button" @click="setPrimary(index)" class="p-1.5 bg-white rounded-full text-yellow-500 hover:scale-110 transition-transform">
                <Star :fill="img.is_primary ? 'currentColor' : 'none'" class="w-4 h-4" />
              </button>
              <button type="button" @click="removeImage(index)" class="p-1.5 bg-white rounded-full text-red-500 hover:scale-110 transition-transform">
                <X class="w-4 h-4" />
              </button>
            </div>

            <div v-if="img.is_primary" class="absolute top-1 left-1 bg-yellow-400 text-white p-0.5 rounded shadow-sm">
              <Star fill="currentColor" class="w-3 h-3" />
            </div>
          </div>

          <label v-if="uploadedImages.length < 5" class="border-2 border-dashed rounded-md flex flex-col items-center justify-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors aspect-square">
            <input type="file" accept="image/*" class="hidden" multiple @change="handleFileSelect" :disabled="isUploading" />
            <div v-if="isUploading" class="flex flex-col items-center">
              <Loader2 class="w-6 h-6 animate-spin text-gray-400" />
              <span class="text-[10px] mt-1 text-gray-400">上傳中</span>
            </div>
            <div v-else class="flex flex-col items-center">
              <Upload class="w-6 h-6 text-gray-400" />
              <span class="text-[10px] mt-1 text-gray-400">新增圖片</span>
            </div>
          </label>
        </div>
        <p class="text-[11px] text-gray-500">支援 JPG, PNG, WEBP。建議尺寸 800x800 px。</p>
      </div>
    </div>

    <div class="flex justify-end gap-3 pt-4 border-t">
      <Button type="button" variant="outline" @click="emit('cancel')" :disabled="isSubmitting">取消</Button>
      <Button type="submit" :disabled="isSubmitting || isUploading">
        <Loader2 v-if="isSubmitting" class="w-4 h-4 mr-2 animate-spin" />
        {{ props.initialValues?.id ? '更新商品' : '建立商品' }}
      </Button>
    </div>
  </form>
</template>
