<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import ForgotPasswordForm from '@/components/auth/ForgotPasswordForm.vue'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'

const { t } = useI18n()
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
    <Navbar />
    
    <main class="flex-grow flex flex-col justify-center px-6 py-12 lg:px-8">
      <div class="sm:mx-auto sm:w-full sm:max-w-sm">
        <h2 class="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900 dark:text-white">
          {{ t('forgotPassword.title') }}
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          {{ t('forgotPassword.description') }}
        </p>
      </div>

      <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
        <ForgotPasswordForm />

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
