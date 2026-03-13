<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { authService } from '@/services/authService'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const token = (route.query.token as string) || ''
const type = (route.query.type as string) || ''
const userId = (route.query.user_id as string) || ''

const status = ref<'verifying' | 'success' | 'pending' | 'failed'>('verifying')
const errorMessage = ref('')
const successMessage = ref('')

onMounted(async () => {
  if (!token) {
    status.value = 'failed'
    errorMessage.value = t('verifyEmail.failed')
    return
  }

  try {
    if (type && userId) {
      // 變更電子郵件驗證
      const result = await authService.verifyEmailChange(token, type, userId)
      
      if (result.status === 'completed') {
        status.value = 'success'
        successMessage.value = t('verifyEmail.changeSuccess')
        // 變更成功後跳轉至個人資料頁
        setTimeout(() => {
          router.push({ name: 'profile' })
        }, 3000)
      } else {
        status.value = 'pending'
        successMessage.value = t('verifyEmail.pending')
      }
    } else {
      // 註冊電子郵件驗證
      await authService.verifyEmail(token)
      status.value = 'success'
      successMessage.value = t('verifyEmail.success')
      
      // 驗證成功後，延遲跳轉至登入頁面
      setTimeout(() => {
        router.push({ name: 'login' })
      }, 3000)
    }
  } catch (error: any) {
    status.value = 'failed'
    errorMessage.value = t(error.message) || t('verifyEmail.failed')
  }
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
    <Navbar />
    
    <main class="flex-grow flex flex-col justify-center px-6 py-12 lg:px-8">
      <div class="sm:mx-auto sm:w-full sm:max-w-sm text-center">
        <h2 class="mt-10 text-2xl font-bold leading-9 tracking-tight text-gray-900 dark:text-white mb-8">
          {{ t('verifyEmail.title') }}
        </h2>
        
        <div v-if="status === 'verifying'" class="flex flex-col items-center">
          <svg class="animate-spin h-10 w-10 text-indigo-600 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="text-gray-600 dark:text-gray-400">{{ t('verifyEmail.verifying') }}</p>
        </div>

        <div v-else-if="status === 'success'" class="p-4 mb-4 text-sm text-green-700 bg-green-100 rounded-lg dark:bg-green-900 dark:text-green-200">
          <p class="font-medium text-lg mb-2">{{ successMessage }}</p>
          <p v-if="!type">{{ t('auth.loginNow') }}...</p>
          <p v-else>{{ t('profile.title') }}...</p>
        </div>

        <div v-else-if="status === 'pending'" class="p-4 mb-4 text-sm text-blue-700 bg-blue-100 rounded-lg dark:bg-blue-900 dark:text-blue-200">
          <p class="font-medium text-lg mb-2">{{ successMessage }}</p>
        </div>

        <div v-else-if="status === 'failed'" class="p-4 mb-4 text-sm text-red-700 bg-red-100 rounded-lg dark:bg-red-900 dark:text-red-200">
          <p>{{ errorMessage }}</p>
        </div>
        
        <p v-if="status !== 'verifying'" class="mt-10 text-center text-sm text-gray-500 dark:text-gray-400">
          <router-link :to="{ name: 'login' }" class="font-semibold leading-6 text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300">
            {{ t('auth.backToLogin') }}
          </router-link>
        </p>
      </div>
    </main>

    <Footer />
  </div>
</template>
