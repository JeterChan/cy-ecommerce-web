<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { useI18n } from 'vue-i18n'
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { ProfileUpdateSchema, ChangePasswordSchema, type ProfileUpdateFormValues, type ChangePasswordFormValues } from '@/models/auth.schema'
import { userService } from '@/services/userService'
import { authService } from '@/services/authService'
import { useRouter } from 'vue-router'
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
  Edit,
  CheckCircle2,
  Save,
  X,
  Lock,
  KeyRound,
  Eye,
  EyeOff
} from 'lucide-vue-next'

const { t } = useI18n()
const authStore = useAuthStore()
const { showSuccess, showError } = useToast()
const router = useRouter()

const isEditing = ref(false)
const isSubmitting = ref(false)

// 變更電子郵件狀態
const isChangingEmail = ref(false)
const newEmail = ref('')
const changeEmailPassword = ref('')
const changeEmailLoading = ref(false)
const changeEmailSuccess = ref(false)

// 修改密碼狀態
const isChangingPassword = ref(false)
const isChangingPasswordSubmitting = ref(false)
const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const showEmailChangePassword = ref(false)

// 載具選項
const carrierTypes = [
  { value: '', label: '請選擇載具類型' },
  { value: 'MOBILE', label: '手機條碼載具' },
  { value: 'CITIZEN_CARD', label: '自然人憑證' },
  { value: 'DONATE', label: '捐贈' },
]

const carrierTypeLabels: Record<string, string> = {
  'MOBILE': '手機條碼載具',
  'CITIZEN_CARD': '自然人憑證',
  'DONATE': '捐贈',
  '': '未設定'
}

// 個人資料表單驗證
const profileFormSchema = toTypedSchema(ProfileUpdateSchema)
const { handleSubmit: handleProfileSubmit, errors: profileErrors, resetForm: resetProfileForm } = useForm<ProfileUpdateFormValues>({
  validationSchema: profileFormSchema
})

const { value: username } = useField<string>('username')
const { value: phone } = useField<string>('phone')
const { value: address } = useField<string>('address')
const { value: carrierType } = useField<string>('carrier_type')
const { value: carrierNumber } = useField<string>('carrier_number')
const { value: taxId } = useField<string>('tax_id')

// 修改密碼表單驗證
const passwordFormSchema = toTypedSchema(ChangePasswordSchema)
const { handleSubmit: handlePasswordSubmit, errors: passwordErrors, resetForm: resetPasswordForm } = useForm<ChangePasswordFormValues>({
  validationSchema: passwordFormSchema
})

const { value: old_password } = useField<string>('old_password')
const { value: new_password } = useField<string>('new_password')
const { value: confirm_password } = useField<string>('confirm_password')

const loadUserData = async () => {
  try {
    await authStore.getCurrentUser()
    const user = authStore.user
    if (user) {
      resetProfileForm({
        values: {
          username: user.username || '',
          phone: user.phone || '',
          address: user.address || '',
          carrier_type: user.carrier_type || '',
          carrier_number: user.carrier_number || '',
          tax_id: user.tax_id || '',
        }
      })
    }
  } catch (error) {
    showError('無法載入使用者資訊')
  }
}

onMounted(loadUserData)

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', { year: 'numeric', month: 'long', day: 'numeric' })
}

const onSaveProfile = handleProfileSubmit(async (values) => {
  try {
    isSubmitting.value = true
    const payload = Object.fromEntries(
      Object.entries(values).map(([k, v]) => [k, v === '' ? undefined : v])
    )
    await authStore.updateProfile(payload as any)
    showSuccess('個人資料更新成功')
    isEditing.value = false
  } catch (error: any) {
    showError(t(error.message) || '更新失敗')
  } finally {
    isSubmitting.value = false
  }
})

const onCancelEdit = () => {
  isEditing.value = false
  loadUserData()
}

const onPasswordSubmit = handlePasswordSubmit(async (values) => {
  try {
    isChangingPasswordSubmitting.value = true
    await authService.changePassword({
      old_password: values.old_password,
      new_password: values.new_password
    })
    showSuccess(t('profile.changePasswordSuccess'))
    isChangingPassword.value = false
    resetPasswordForm()
  } catch (error: any) {
    showError(t(error.message) || '密碼修改失敗')
  } finally {
    isChangingPasswordSubmitting.value = false
  }
})

const handleRequestEmailChange = async () => {
  if (!newEmail.value || !changeEmailPassword.value) {
    showError('請填寫新電子郵件和目前密碼')
    return
  }
  try {
    changeEmailLoading.value = true
    await authService.requestEmailChange({
      new_email: newEmail.value,
      password: changeEmailPassword.value,
    })
    changeEmailSuccess.value = true
  } catch (err: any) {
    showError(err?.response?.data?.detail || '請求失敗，請確認密碼是否正確')
  } finally {
    changeEmailLoading.value = false
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
          <div class="flex gap-2">
            <template v-if="!isEditing">
              <Button @click="isEditing = true" variant="outline" class="flex items-center gap-2">
                <Edit class="h-4 w-4" /> 編輯資料
              </Button>
            </template>
            <template v-else>
              <Button @click="onSaveProfile" :disabled="isSubmitting" class="flex items-center gap-2">
                <Loader2 v-if="isSubmitting" class="h-4 w-4 animate-spin" />
                <Save v-else class="h-4 w-4" /> 儲存變更
              </Button>
              <Button @click="onCancelEdit" variant="outline" :disabled="isSubmitting" class="flex items-center gap-2">
                <X class="h-4 w-4" /> 取消
              </Button>
            </template>
          </div>
        </div>

        <div class="space-y-6">
          <!-- 帳號資訊卡片 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2"><UserIcon class="h-5 w-5" /> 帳號資訊</CardTitle>
              <CardDescription>您的帳戶基本登入與驗證資訊</CardDescription>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-2">
                  <Label :for="isEditing ? 'username' : ''" class="text-muted-foreground flex items-center gap-1">
                    <UserIcon class="h-3 w-3" /> 使用者名稱
                  </Label>
                  <Input v-if="isEditing" id="username" v-model="username" />
                  <p v-else class="font-medium px-3 py-2 bg-muted rounded-md">{{ authStore.user?.username }}</p>
                  <p v-if="profileErrors.username" class="text-xs text-red-500">{{ t('validation.' + profileErrors.username) }}</p>
                </div>
                <div class="space-y-2">
                  <Label class="text-muted-foreground flex items-center gap-1"><Calendar class="h-3 w-3" /> 註冊日期</Label>
                  <p class="font-medium px-3 py-2 bg-muted rounded-md">{{ formatDate(authStore.user?.created_at || '') }}</p>
                </div>
              </div>

              <div class="space-y-2">
                <Label class="text-muted-foreground flex items-center gap-1"><Mail class="h-3 w-3" /> 電子郵件</Label>
                <div class="flex items-center justify-between px-3 py-2 bg-muted rounded-md">
                  <span class="font-medium">{{ authStore.user?.email }}</span>
                  <span v-if="authStore.user?.is_verified" class="text-xs text-green-600 flex items-center gap-1">
                    <CheckCircle2 class="h-3 w-3" /> 已驗證
                  </span>
                </div>
                
                <div v-if="!changeEmailSuccess">
                  <button v-if="!isChangingEmail" @click="isChangingEmail = true" class="text-xs text-blue-600 hover:underline">變更電子郵件</button>
                  <div v-else class="mt-3 space-y-3 p-4 border rounded-md bg-muted/30">
                    <div class="grid gap-2">
                      <Label>新電子郵件</Label>
                      <Input v-model="newEmail" type="email" :disabled="changeEmailLoading" />
                    </div>
                    <div class="grid gap-2">
                      <Label>目前密碼</Label>
                      <div class="relative">
                        <Input v-model="changeEmailPassword" :type="showEmailChangePassword ? 'text' : 'password'" :disabled="changeEmailLoading" class="pr-10" />
                        <button type="button" @click="showEmailChangePassword = !showEmailChangePassword" class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600">
                          <Eye v-if="!showEmailChangePassword" class="h-4 w-4" />
                          <EyeOff v-else class="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                    <div class="flex gap-2">
                      <Button size="sm" @click="handleRequestEmailChange" :disabled="changeEmailLoading">
                        <Loader2 v-if="changeEmailLoading" class="h-3 w-3 animate-spin mr-1" /> 送出
                      </Button>
                      <Button size="sm" variant="ghost" @click="isChangingEmail = false">取消</Button>
                    </div>
                  </div>
                </div>
                <Alert v-else class="bg-green-50 border-green-200 mt-2"><AlertDescription class="text-green-800">驗證信已發送，請至新舊信箱確認。</AlertDescription></Alert>
              </div>
            </CardContent>
          </Card>

          <!-- 安全設定卡片 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2"><Lock class="h-5 w-5" /> {{ t('profile.securitySettings') }}</CardTitle>
              <CardDescription>管理您的帳號安全與密碼</CardDescription>
            </CardHeader>
            <CardContent>
              <div v-if="!isChangingPassword">
                <Button variant="outline" size="sm" @click="isChangingPassword = true" class="flex items-center gap-2">
                  <KeyRound class="h-4 w-4" /> {{ t('profile.changePassword') }}
                </Button>
              </div>
              <form v-else @submit.prevent="onPasswordSubmit" class="space-y-4">
                <div class="grid gap-4">
                  <div class="space-y-2">
                    <Label for="old_password">{{ t('profile.oldPassword') }}</Label>
                    <div class="relative">
                      <Input id="old_password" v-model="old_password" :type="showOldPassword ? 'text' : 'password'" />
                      <button type="button" @click="showOldPassword = !showOldPassword" class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600">
                        <Eye v-if="!showOldPassword" class="h-4 w-4" />
                        <EyeOff v-else class="h-4 w-4" />
                      </button>
                    </div>
                    <p v-if="passwordErrors.old_password" class="text-xs text-red-500">{{ t('validation.' + passwordErrors.old_password) }}</p>
                  </div>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                      <Label for="new_password">{{ t('profile.newPassword') }}</Label>
                      <div class="relative">
                        <Input id="new_password" v-model="new_password" :type="showNewPassword ? 'text' : 'password'" />
                        <button type="button" @click="showNewPassword = !showNewPassword" class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600">
                          <Eye v-if="!showNewPassword" class="h-4 w-4" />
                          <EyeOff v-else class="h-4 w-4" />
                        </button>
                      </div>
                      <p v-if="passwordErrors.new_password" class="text-xs text-red-500">{{ t('validation.' + passwordErrors.new_password) }}</p>
                    </div>
                    <div class="space-y-2">
                      <Label for="confirm_password">{{ t('profile.confirmNewPassword') }}</Label>
                      <div class="relative">
                        <Input id="confirm_password" v-model="confirm_password" :type="showConfirmPassword ? 'text' : 'password'" />
                        <button type="button" @click="showConfirmPassword = !showConfirmPassword" class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600">
                          <Eye v-if="!showConfirmPassword" class="h-4 w-4" />
                          <EyeOff v-else class="h-4 w-4" />
                        </button>
                      </div>
                      <p v-if="passwordErrors.confirm_password" class="text-xs text-red-500">{{ t('validation.' + passwordErrors.confirm_password) }}</p>
                    </div>
                  </div>
                </div>
                <div class="flex gap-2 justify-end">
                  <Button type="button" variant="ghost" size="sm" @click="isChangingPassword = false">取消</Button>
                  <Button type="submit" size="sm" :disabled="isChangingPasswordSubmitting">
                    <Loader2 v-if="isChangingPasswordSubmitting" class="h-3 w-3 animate-spin mr-1" /> 儲存新密碼
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          <!-- 個人資料卡片 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2"><Phone class="h-5 w-5" /> 個人資料</CardTitle>
            </CardHeader>
            <CardContent class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label :for="isEditing ? 'phone' : ''" class="text-muted-foreground">聯絡電話</Label>
                <Input v-if="isEditing" id="phone" v-model="phone" type="tel" />
                <p v-else class="font-medium px-3 py-2 bg-muted rounded-md">{{ authStore.user?.phone || '未設定' }}</p>
                <p v-if="profileErrors.phone" class="text-xs text-red-500">{{ t('validation.' + profileErrors.phone) }}</p>
              </div>
              <div class="space-y-2">
                <Label :for="isEditing ? 'address' : ''" class="text-muted-foreground">郵寄地址</Label>
                <Input v-if="isEditing" id="address" v-model="address" />
                <p v-else class="font-medium px-3 py-2 bg-muted rounded-md">{{ authStore.user?.address || '未設定' }}</p>
              </div>
            </CardContent>
          </Card>

          <!-- 發票資訊卡片 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2"><CreditCard class="h-5 w-5" /> 發票資訊</CardTitle>
            </CardHeader>
            <CardContent class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label class="text-muted-foreground">載具類型</Label>
                <select v-if="isEditing" v-model="carrierType" class="w-full h-10 px-3 py-2 border rounded-md dark:bg-gray-800">
                  <option v-for="opt in carrierTypes" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
                <p v-else class="font-medium px-3 py-2 bg-muted rounded-md">{{ carrierTypeLabels[authStore.user?.carrier_type || ''] }}</p>
              </div>
              <div class="space-y-2">
                <Label :for="isEditing ? 'carrier_number' : ''" class="text-muted-foreground">載具號碼</Label>
                <Input v-if="isEditing" id="carrier_number" v-model="carrierNumber" />
                <p v-else class="font-medium px-3 py-2 bg-muted rounded-md">{{ authStore.user?.carrier_number || '未設定' }}</p>
              </div>
              <div class="space-y-2">
                <Label :for="isEditing ? 'tax_id' : ''" class="text-muted-foreground">統一編號</Label>
                <Input v-if="isEditing" id="tax_id" v-model="taxId" maxlength="8" />
                <p v-else class="font-medium px-3 py-2 bg-muted rounded-md">{{ authStore.user?.tax_id || '未設定' }}</p>
                <p v-if="profileErrors.tax_id" class="text-xs text-red-500">{{ t('validation.' + profileErrors.tax_id) }}</p>
              </div>
            </CardContent>
          </Card>

          <!-- 操作按鈕 (僅在編輯模式下顯示於底部) -->
          <div v-if="isEditing" class="flex justify-end gap-3 pt-4">
            <Button @click="onCancelEdit" variant="outline" :disabled="isSubmitting" class="flex items-center gap-2">
              <X class="h-4 w-4" /> 取消
            </Button>
            <Button @click="onSaveProfile" :disabled="isSubmitting" class="flex items-center gap-2">
              <Loader2 v-if="isSubmitting" class="h-4 w-4 animate-spin" />
              <Save v-else class="h-4 w-4" /> 儲存變更
            </Button>
          </div>
        </div>
      </div>
    </main>
    <Footer />
  </div>
</template>
