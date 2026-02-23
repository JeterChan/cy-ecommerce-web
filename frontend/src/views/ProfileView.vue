<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import type { User } from '@/types/auth'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Loader2,
  User as UserIcon,
  Mail,
  Calendar,
  Phone,
  MapPin,
  CreditCard,
  FileText,
  Save,
  X,
  Edit
} from 'lucide-vue-next'

const authStore = useAuthStore()
const { showSuccess, showError } = useToast()

const loading = ref(false)
const isEditing = ref(false)

// 基本資訊（唯讀）
const username = ref('')
const email = ref('')
const createdAt = ref('')

// 個人檔案欄位（可編輯）
const phone = ref('')
const address = ref('')
const carrierType = ref('')
const carrierNumber = ref('')
const taxId = ref('')

// 載具類型選項
const carrierTypes = [
  { value: '', label: '請選擇載具類型' },
  { value: 'MOBILE', label: '手機條碼載具' },
  { value: 'CITIZEN_CARD', label: '自然人憑證' },
  { value: 'DONATE', label: '捐贈' },
]

onMounted(async () => {
  await loadUserData()
})

const loadUserData = async () => {
  const currentUser = authStore.user as User | null
  if (currentUser) {
    setUserData(currentUser)
  } else {
    try {
      await authStore.getCurrentUser()
      const user = authStore.user as User | null
      if (user) {
        setUserData(user)
      }
    } catch (error) {
      console.error('Failed to load user info:', error)
      showError('無法載入使用者資訊')
    }
  }
}

const setUserData = (user: User) => {
  username.value = user.username
  email.value = user.email
  createdAt.value = user.created_at
  phone.value = user.phone || ''
  address.value = user.address || ''
  carrierType.value = user.carrier_type || ''
  carrierNumber.value = user.carrier_number || ''
  taxId.value = user.tax_id || ''
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const handleEditToggle = () => {
  if (isEditing.value) {
    const user = authStore.user as User | null
    if (user) {
      setUserData(user)
    }
  }
  isEditing.value = !isEditing.value
}

const handleSaveProfile = async () => {
  try {
    loading.value = true

    await authStore.updateProfile({
      phone: phone.value || undefined,
      address: address.value || undefined,
      carrier_type: carrierType.value || undefined,
      carrier_number: carrierNumber.value || undefined,
      tax_id: taxId.value || undefined,
    })

    showSuccess('個人檔案已更新')
    isEditing.value = false
  } catch (error: any) {
    console.error('Profile update error:', error)
    showError(error.response?.data?.detail || '更新失敗，請稍後再試')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col">
    <Navbar />
    <main class="flex-grow container mx-auto py-8 px-4">
      <div class="max-w-3xl mx-auto">
        <div class="flex justify-between items-center mb-8">
          <h1 class="text-3xl font-bold">個人檔案</h1>
          <Button
            v-if="!isEditing"
            @click="handleEditToggle"
            variant="outline"
            class="flex items-center gap-2"
          >
            <Edit class="h-4 w-4" />
            編輯資料
          </Button>
        </div>

        <!-- 基本資訊卡片 -->
        <Card class="mb-6">
          <CardHeader>
            <CardTitle class="flex items-center gap-2">
              <UserIcon class="h-5 w-5" />
              基本資訊
            </CardTitle>
            <CardDescription>您的帳戶基本資訊（不可修改）</CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="space-y-2">
              <Label class="flex items-center gap-2">
                <UserIcon class="h-4 w-4" />
                使用者名稱
              </Label>
              <Input :value="username" disabled class="bg-muted" />
            </div>

            <div class="space-y-2">
              <Label class="flex items-center gap-2">
                <Mail class="h-4 w-4" />
                電子郵件
              </Label>
              <Input :value="email" disabled class="bg-muted" />
            </div>

            <div class="space-y-2">
              <Label class="flex items-center gap-2">
                <Calendar class="h-4 w-4" />
                註冊日期
              </Label>
              <Input :value="formatDate(createdAt)" disabled class="bg-muted" />
            </div>
          </CardContent>
        </Card>

        <!-- 個人資料卡片 -->
        <Card class="mb-6">
          <CardHeader>
            <CardTitle class="flex items-center gap-2">
              <Phone class="h-5 w-5" />
              個人資料
            </CardTitle>
            <CardDescription>您的聯絡方式和郵寄地址</CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="space-y-2">
              <Label class="flex items-center gap-2">
                <Phone class="h-4 w-4" />
                聯絡電話
              </Label>
              <Input
                v-model="phone"
                :disabled="!isEditing"
                :class="{ 'bg-muted': !isEditing }"
                placeholder="例如：0912345678"
                type="tel"
              />
            </div>

            <div class="space-y-2">
              <Label class="flex items-center gap-2">
                <MapPin class="h-4 w-4" />
                郵寄地址
              </Label>
              <Input
                v-model="address"
                :disabled="!isEditing"
                :class="{ 'bg-muted': !isEditing }"
                placeholder="例如：台北市信義區信義路五段7號"
              />
            </div>
          </CardContent>
        </Card>

        <!-- 發票資訊卡片 -->
        <Card class="mb-6">
          <CardHeader>
            <CardTitle class="flex items-center gap-2">
              <CreditCard class="h-5 w-5" />
              發票資訊
            </CardTitle>
            <CardDescription>電子發票載具和統一編號</CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="space-y-2">
              <Label>載具類型</Label>
              <select
                v-model="carrierType"
                :disabled="!isEditing"
                :class="[
                  'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500',
                  { 'bg-muted cursor-not-allowed': !isEditing }
                ]"
              >
                <option v-for="type in carrierTypes" :key="type.value" :value="type.value">
                  {{ type.label }}
                </option>
              </select>
            </div>

            <div class="space-y-2">
              <Label class="flex items-center gap-2">
                <CreditCard class="h-4 w-4" />
                載具號碼
              </Label>
              <Input
                v-model="carrierNumber"
                :disabled="!isEditing"
                :class="{ 'bg-muted': !isEditing }"
                placeholder="例如：/ABC1234"
              />
              <p class="text-xs text-muted-foreground">
                手機條碼載具格式：/XXXXXXX（7碼英數字）
              </p>
            </div>

            <Separator />

            <div class="space-y-2">
              <Label class="flex items-center gap-2">
                <FileText class="h-4 w-4" />
                統一編號
              </Label>
              <Input
                v-model="taxId"
                :disabled="!isEditing"
                :class="{ 'bg-muted': !isEditing }"
                placeholder="例如：12345678"
                maxlength="8"
              />
              <p class="text-xs text-muted-foreground">
                若需開立公司發票，請填寫統一編號（8碼數字）
              </p>
            </div>
          </CardContent>
        </Card>

        <!-- 操作按鈕 -->
        <div v-if="isEditing" class="flex gap-3">
          <Button
            @click="handleSaveProfile"
            :disabled="loading"
            class="flex items-center gap-2"
          >
            <Loader2 v-if="loading" class="h-4 w-4 animate-spin" />
            <Save v-else class="h-4 w-4" />
            儲存變更
          </Button>
          <Button
            @click="handleEditToggle"
            variant="outline"
            :disabled="loading"
            class="flex items-center gap-2"
          >
            <X class="h-4 w-4" />
            取消
          </Button>
        </div>

        <Alert class="mt-6">
          <AlertDescription>
            <strong>提示：</strong>個人資料將用於訂單配送和發票開立。載具資訊可在結帳時使用，統一編號用於開立公司發票。
          </AlertDescription>
        </Alert>
      </div>
    </main>
    <Footer />
  </div>
</template>

