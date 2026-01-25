<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'

const { t } = useI18n()
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <Card class="w-full max-w-md">
      <CardHeader>
        <CardTitle class="text-2xl font-bold text-center">
          {{ t('forgotPassword.title') }}
        </CardTitle>
      </CardHeader>

      <CardContent>
        <p class="text-center text-gray-600">
          {{ t('forgotPassword.developmentMessage') }}
        </p>
      </CardContent>

      <CardFooter class="flex justify-center">
        <Button as-child>
          <RouterLink to="/login">
            {{ t('auth.backToLogin') }}
          </RouterLink>
        </Button>
      </CardFooter>
    </Card>
  </div>
</template>

