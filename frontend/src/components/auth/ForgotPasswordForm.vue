<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { ForgotPasswordSchema, type ForgotPasswordFormValues } from '@/models/auth.schema'
import { authService } from '@/services/authService'

const { t } = useI18n()
const emit = defineEmits<{
  (e: 'success'): void
}>()

const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const formSchema = toTypedSchema(ForgotPasswordSchema)
const { handleSubmit, errors } = useForm<ForgotPasswordFormValues>({
  validationSchema: formSchema,
})

const { value: email } = useField<string>('email')

const onSubmit = handleSubmit(async (values) => {
  try {
    isSubmitting.value = true
    errorMessage.value = ''
    successMessage.value = ''
    
    await authService.forgotPassword(values)
    successMessage.value = t('forgotPassword.sendSuccess')
    emit('success')
  } catch (error: any) {
    errorMessage.value = t(error.message)
  } finally {
    isSubmitting.value = false
  }
})
</script>

<template>
  <form @submit.prevent="onSubmit" class="space-y-6">
    <div v-if="errorMessage" class="p-3 text-sm text-red-600 bg-red-50 rounded-md dark:bg-red-900/50 dark:text-red-200">
      {{ errorMessage }}
    </div>
    
    <div v-if="successMessage" class="p-3 text-sm text-green-600 bg-green-50 rounded-md dark:bg-green-900/50 dark:text-green-200">
      {{ successMessage }}
    </div>

    <div>
      <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ t('auth.email') }}
      </label>
      <div class="mt-1">
        <input
          id="email"
          v-model="email"
          type="email"
          autocomplete="email"
          :disabled="isSubmitting || !!successMessage"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          :class="{ 'border-red-500 focus:ring-red-500 focus:border-red-500': errors.email }"
        />
      </div>
      <p v-if="errors.email" class="mt-1 text-sm text-red-600">{{ t('validation.' + errors.email) }}</p>
    </div>

    <div>
      <button
        type="submit"
        :disabled="isSubmitting || !!successMessage"
        class="flex justify-center w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="isSubmitting" class="mr-2">...</span>
        {{ t('forgotPassword.sendEmail') }}
      </button>
    </div>
  </form>
</template>
