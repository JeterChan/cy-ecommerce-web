<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ResetPasswordForm from '@/components/auth/ResetPasswordForm.vue'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'

const route = useRoute()
const { t } = useI18n()

// 從 query parameter 獲取 token
const token = (route.query.token as string) || ''
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
    <Navbar />
    
    <main class="flex-grow flex flex-col justify-center px-6 py-12 lg:px-8">
      <div class="sm:mx-auto sm:w-full sm:max-w-sm">
        <h2 class="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900 dark:text-white">
          {{ t('resetPassword.title') }}
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          {{ t('resetPassword.description') }}
        </p>
      </div>

      <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
        <div v-if="!token" class="p-4 mb-4 text-sm text-red-700 bg-red-100 rounded-lg dark:bg-red-900 dark:text-red-200">
          {{ t('resetPassword.invalidToken') }}
        </div>
        <ResetPasswordForm v-else :token="token" />

        <p class="mt-10 text-center text-sm text-gray-500 dark:text-gray-400">
          <router-link :to="{ name: 'login' }" class="font-semibold leading-6 text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300">
            {{ t('auth.backToLogin') }}
          </router-link>
        </p>
      </div>
    </main>

    <Footer />
  </div>
</template>
