<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Loader2, CheckCircle2, Clock, XCircle } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import { authService } from '@/services/authService'

type VerifyStatus = 'loading' | 'pending' | 'completed' | 'error'

const route = useRoute()
const router = useRouter()

const status = ref<VerifyStatus>('loading')
const errorMessage = ref('')

onMounted(async () => {
  const token = route.query.token as string
  const type = route.query.type as string
  const userId = route.query.user_id as string

  if (!token || !type || !userId) {
    status.value = 'error'
    errorMessage.value = '無效的驗證連結，缺少必要參數。'
    return
  }

  try {
    const result = await authService.verifyEmailChange(token, type, userId)
    status.value = result.status === 'completed' ? 'completed' : 'pending'
  } catch (err: any) {
    status.value = 'error'
    const detail = err?.response?.data?.detail
    errorMessage.value = detail || '驗證失敗，連結可能已過期或無效。'
  }
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <Navbar />

    <main class="flex-1 flex items-center justify-center py-12 px-4">
      <Card class="w-full max-w-md text-center">
        <CardHeader>
          <CardTitle class="text-2xl font-bold">電子郵件驗證</CardTitle>
          <CardDescription>正在處理您的電子郵件變更請求</CardDescription>
        </CardHeader>

        <CardContent class="flex flex-col items-center gap-6 py-6">
          <!-- Loading -->
          <template v-if="status === 'loading'">
            <Loader2 class="h-16 w-16 text-blue-500 animate-spin" />
            <p class="text-gray-600">驗證中，請稍候…</p>
          </template>

          <!-- Pending: one side verified, waiting for the other -->
          <template v-else-if="status === 'pending'">
            <Clock class="h-16 w-16 text-amber-500" />
            <div>
              <p class="text-lg font-semibold text-amber-700">驗證完成，等待另一端確認</p>
              <p class="mt-2 text-sm text-gray-500">
                此信箱已完成驗證。請點擊寄送至另一個信箱的驗證連結以完成電子郵件變更。
              </p>
            </div>
            <Button variant="outline" @click="router.push('/')">返回首頁</Button>
          </template>

          <!-- Completed: both sides verified, email changed -->
          <template v-else-if="status === 'completed'">
            <CheckCircle2 class="h-16 w-16 text-green-500" />
            <div>
              <p class="text-lg font-semibold text-green-700">電子郵件已成功更新！</p>
              <p class="mt-2 text-sm text-gray-500">
                兩端驗證均已完成，您的帳號電子郵件已更新。
              </p>
            </div>
            <Button @click="router.push('/profile')">前往個人檔案</Button>
          </template>

          <!-- Error -->
          <template v-else-if="status === 'error'">
            <XCircle class="h-16 w-16 text-red-500" />
            <div>
              <p class="text-lg font-semibold text-red-700">驗證失敗</p>
              <p class="mt-2 text-sm text-gray-500">{{ errorMessage }}</p>
            </div>
            <Button variant="outline" @click="router.push('/')">返回首頁</Button>
          </template>
        </CardContent>
      </Card>
    </main>

    <Footer />
  </div>
</template>
