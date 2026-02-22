<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
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
import { useToast } from '@/composables/useToast'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const { showSuccess, showError } = useToast()

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const isLoading = ref(false)

// Zod 驗證 Schema - 使用 computed 讓翻譯可以響應式更新
const registerSchema = computed(() => toTypedSchema(
  z.object({
    username: z
      .string({ required_error: t('validation.required') })
      .min(1, t('validation.required'))
      .min(3, t('validation.usernameMinLength'))
      .max(50, t('validation.usernameMaxLength'))
      .regex(/^[a-zA-Z0-9_-]+$/, t('validation.usernameInvalid'))
      .refine(
        (val) => !val.startsWith('_') && !val.startsWith('-') && !val.endsWith('_') && !val.endsWith('-'),
        { message: t('validation.usernameFormat') }
      ),
    email: z
      .string({ required_error: t('validation.required') })
      .min(1, t('validation.required'))
      .email(t('validation.emailInvalid')),
    password: z
      .string({ required_error: t('validation.required') })
      .min(1, t('validation.required'))
      .min(8, t('validation.passwordMinLength'))
      .regex(
        /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).+$/,
        t('validation.passwordStrength')
      ),
    confirmPassword: z
      .string({ required_error: t('validation.required') })
      .min(1, t('validation.required'))
  }).refine((data) => data.password === data.confirmPassword, {
    message: t('validation.passwordMismatch'),
    path: ['confirmPassword']
  })
))

const { defineField, handleSubmit, errors } = useForm({
  validationSchema: registerSchema
})

const [username, usernameAttrs] = defineField('username')
const [email, emailAttrs] = defineField('email')
const [password, passwordAttrs] = defineField('password')
const [confirmPassword, confirmPasswordAttrs] = defineField('confirmPassword')

const onSubmit = handleSubmit(async (values) => {
  isLoading.value = true

  try {
    await authStore.register(values.username, values.email, values.password)
    showSuccess(t('auth.registerSuccess'))
    router.push('/login')
  } catch (error: any) {
    // 處理不同類型的錯誤
    let message = t('error.generic')

    if (error.response) {
      // 伺服器回應錯誤（4xx, 5xx）
      message = error.response.data?.detail || t('error.generic')
    } else if (error.request) {
      // 請求已發送但沒有收到回應（網路錯誤）
      message = t('error.networkError')
    }

    showError(message)
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
        <CardTitle class="text-2xl font-bold text-center">{{ t('auth.register') }}</CardTitle>
        <CardDescription class="text-center">
          {{ t('auth.haveAccount') }}
          <RouterLink to="/login" class="text-primary hover:underline">
            {{ t('auth.loginNow') }}
          </RouterLink>
        </CardDescription>
      </CardHeader>

      <form @submit="onSubmit">
        <CardContent class="space-y-4">
          <!-- Username -->
          <div class="space-y-2">
            <label for="username" class="text-sm font-medium">
              {{ t('auth.username') }}
            </label>
            <Input
              id="username"
              v-model="username"
              v-bind="usernameAttrs"
              type="text"
              :placeholder="t('auth.username')"
              autocomplete="username"
            />
            <p v-if="errors.username" class="text-sm text-red-500">
              {{ errors.username }}
            </p>
          </div>

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
                autocomplete="new-password"
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

          <!-- Confirm Password -->
          <div class="space-y-2">
            <label for="confirmPassword" class="text-sm font-medium">
              {{ t('auth.confirmPassword') }}
            </label>
            <div class="relative">
              <Input
                id="confirmPassword"
                v-model="confirmPassword"
                v-bind="confirmPasswordAttrs"
                :type="showConfirmPassword ? 'text' : 'password'"
                :placeholder="t('auth.confirmPassword')"
                autocomplete="new-password"
                class="pr-10"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
              >
                <Eye v-if="!showConfirmPassword" class="h-5 w-5" />
                <EyeOff v-else class="h-5 w-5" />
              </button>
            </div>
            <p v-if="errors.confirmPassword" class="text-sm text-red-500">
              {{ errors.confirmPassword }}
            </p>
          </div>
        </CardContent>

        <CardFooter>
          <Button type="submit" class="w-full" :disabled="isLoading">
            {{ isLoading ? '註冊中...' : t('auth.register') }}
          </Button>
        </CardFooter>
      </form>
    </Card>
  </div>

  <Footer />
  </div>
</template>

