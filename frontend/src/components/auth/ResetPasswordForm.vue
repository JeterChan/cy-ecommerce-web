<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { ResetPasswordSchema, type ResetPasswordFormValues } from '@/models/auth.schema'
import { authService } from '@/services/authService'
import { useRouter } from 'vue-router'
import { Eye, EyeOff } from 'lucide-vue-next'

const props = defineProps<{
  token: string
}>()

const { t } = useI18n()
const router = useRouter()
const emit = defineEmits<{
  (e: 'success'): void
}>()

const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const formSchema = toTypedSchema(ResetPasswordSchema)
const { handleSubmit, errors } = useForm<ResetPasswordFormValues>({
  validationSchema: formSchema,
})

const { value: password } = useField<string>('password')
const { value: confirmPassword } = useField<string>('confirmPassword')

const onSubmit = handleSubmit(async (values) => {
  try {
    isSubmitting.value = true
    errorMessage.value = ''
    successMessage.value = ''
    
    await authService.resetPassword(props.token, {
      password: values.password
    })
    
    successMessage.value = t('resetPassword.success')
    emit('success')
    
    setTimeout(() => {
      router.push({ name: 'login' })
    }, 2000)
    
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
      <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ t('resetPassword.newPassword') }}
      </label>
      <div class="mt-1 relative">
        <input
          id="password"
          v-model="password"
          :type="showPassword ? 'text' : 'password'"
          autocomplete="new-password"
          :disabled="isSubmitting || !!successMessage"
          class="block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          :class="{ 'border-red-500 focus:ring-red-500 focus:border-red-500': errors.password }"
        />
        <button type="button" @click="showPassword = !showPassword" class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600">
          <Eye v-if="!showPassword" class="h-4 w-4" />
          <EyeOff v-else class="h-4 w-4" />
        </button>
      </div>
      <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ t('validation.' + errors.password) }}</p>
    </div>

    <div>
      <label for="confirmPassword" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ t('resetPassword.confirmNewPassword') }}
      </label>
      <div class="mt-1 relative">
        <input
          id="confirmPassword"
          v-model="confirmPassword"
          :type="showConfirmPassword ? 'text' : 'password'"
          autocomplete="new-password"
          :disabled="isSubmitting || !!successMessage"
          class="block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          :class="{ 'border-red-500 focus:ring-red-500 focus:border-red-500': errors.confirmPassword }"
        />
        <button type="button" @click="showConfirmPassword = !showConfirmPassword" class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600">
          <Eye v-if="!showConfirmPassword" class="h-4 w-4" />
          <EyeOff v-else class="h-4 w-4" />
        </button>
      </div>
      <p v-if="errors.confirmPassword" class="mt-1 text-sm text-red-600">{{ t('validation.' + errors.confirmPassword) }}</p>
    </div>

    <div>
      <button
        type="submit"
        :disabled="isSubmitting || !!successMessage"
        class="flex justify-center w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="isSubmitting" class="mr-2">...</span>
        {{ t('resetPassword.submit') }}
      </button>
    </div>
  </form>
</template>
