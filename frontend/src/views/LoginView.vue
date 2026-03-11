<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import * as z from 'zod'
import { Eye, EyeOff } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const authStore = useAuthStore()
const cartStore = useCartStore()
const { showSuccess, showError } = useToast()

const showPassword = ref(false)
const isLoading = ref(false)

// Zod 驗證 Schema - 使用 computed 讓翻譯可以響應式更新
const loginSchema = computed(() => toTypedSchema(
  z.object({
    email: z.string({ required_error: t('validation.required') }).min(1, t('validation.required')).email(t('validation.emailInvalid')),
    password: z.string({ required_error: t('validation.required') }).min(1, t('validation.required')).min(8, t('validation.passwordMinLength')),
    rememberMe: z.boolean()
  })
))

const { defineField, handleSubmit, errors } = useForm({
  validationSchema: loginSchema,
  initialValues: {
    rememberMe: false
  }
})

const [email, emailAttrs] = defineField('email')
const [password, passwordAttrs] = defineField('password')
const [rememberMe, rememberMeAttrs] = defineField('rememberMe')

const onSubmit = handleSubmit(async (values) => {
  isLoading.value = true

  try {
    await authStore.login(values.email, values.password, values.rememberMe)
    showSuccess(t('auth.loginSuccess'))

    // 🔄 登入成功後，同步購物車
    console.log('🔄 [Login] 登入成功，開始同步購物車...')
    try {
      await cartStore.syncFromBackend()
      console.log('✅ [Login] 購物車同步完成')
    } catch (cartError) {
      console.warn('⚠️ [Login] 購物車同步失敗，但不影響登入:', cartError)
    }

    // 導向 redirect 參數指定的路徑，或預設首頁
    const redirectPath = (route.query.redirect as string) || '/'
    router.push(redirectPath)
  } catch (error: any) {
    const status = error.response?.status
    if (status === 403) {
      showError(t('error.emailNotVerified'))
    } else {
      showError(t('error.invalidCredentials'))
    }
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <Navbar />

    <div class="flex-1 flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card class="w-full max-w-md">
      <CardHeader>
        <CardTitle class="text-2xl font-bold text-center">{{ t('auth.login') }}</CardTitle>
        <CardDescription class="text-center">
          {{ t('auth.noAccount') }}
          <RouterLink to="/register" class="text-primary hover:underline">
            {{ t('auth.registerNow') }}
          </RouterLink>
        </CardDescription>
      </CardHeader>

      <form @submit="onSubmit">
        <CardContent class="space-y-4">
          <!-- Email -->
          <div class="space-y-2">
            <label for="email" class="text-sm font-medium">
              {{ t('auth.email') }}
            </label>
            <Input
              id="email"
              v-model="email"
              v-bind="emailAttrs"
              type="email"
              :placeholder="t('auth.email')"
              autocomplete="email"
            />
            <p v-if="errors.email" class="text-sm text-red-500">
              {{ errors.email }}
            </p>
          </div>

          <!-- Password -->
          <div class="space-y-2">
            <label for="password" class="text-sm font-medium">
              {{ t('auth.password') }}
            </label>
            <div class="relative">
              <Input
                id="password"
                v-model="password"
                v-bind="passwordAttrs"
                :type="showPassword ? 'text' : 'password'"
                :placeholder="t('auth.password')"
                autocomplete="current-password"
                class="pr-10"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
              >
                <Eye v-if="!showPassword" class="h-5 w-5" />
                <EyeOff v-else class="h-5 w-5" />
              </button>
            </div>
            <p v-if="errors.password" class="text-sm text-red-500">
              {{ errors.password }}
            </p>
          </div>

          <!-- Remember Me & Forgot Password -->
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <input
                id="rememberMe"
                v-model="rememberMe"
                v-bind="rememberMeAttrs"
                type="checkbox"
                class="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <label for="rememberMe" class="text-sm font-medium cursor-pointer">
                {{ t('auth.rememberMe') }}
              </label>
            </div>
            <RouterLink to="/auth/forgot-password" class="text-sm text-primary hover:underline">
              {{ t('auth.forgotPassword') }}
            </RouterLink>
          </div>
        </CardContent>

        <CardFooter>
          <Button type="submit" class="w-full" :disabled="isLoading">
            {{ isLoading ? '登入中...' : t('auth.login') }}
          </Button>
        </CardFooter>
      </form>
    </Card>
  </div>

  <Footer />
  </div>
</template>

