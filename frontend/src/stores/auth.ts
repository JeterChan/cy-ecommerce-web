import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/lib/api'
import type { User, LoginResponse, RegisterResponse } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isInitialized = ref(false)

  // 初始化 Promise，用於等待初始化完成
  let initPromise: Promise<void> | null = null

  // Computed
  const isAuthenticated = computed(() => {
    // 只要有 accessToken 就認為已認證
    // user 資訊可能還在載入中或暫時獲取失敗
    return !!accessToken.value
  })

  // Actions
  const register = async (username: string, email: string, password: string): Promise<void> => {
    try {
      await api.post<RegisterResponse>('/api/v1/auth/register', {
        username,
        email,
        password
      })

      // 註冊成功，不自動登入
      return Promise.resolve()
    } catch (error: any) {
      return Promise.reject(error)
    }
  }

  const login = async (email: string, password: string, rememberMe: boolean): Promise<void> => {
    try {
      const response = await api.post<LoginResponse>('/api/v1/auth/login', {
        email,
        password,
        remember_me: rememberMe
      })

      const { access_token, refresh_token, user: userData } = response.data

      // 更新狀態
      accessToken.value = access_token
      refreshToken.value = refresh_token || null
      user.value = userData

      // 依據 rememberMe 選擇儲存位置
      if (rememberMe) {
        localStorage.setItem('accessToken', access_token)
        if (refresh_token) {
          localStorage.setItem('refreshToken', refresh_token)
        }
      } else {
        sessionStorage.setItem('accessToken', access_token)
        if (refresh_token) {
          sessionStorage.setItem('refreshToken', refresh_token)
        }
      }

      return Promise.resolve()
    } catch (error: any) {
      return Promise.reject(error)
    }
  }

  const logout = (): void => {
    // 清除所有 storage
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    sessionStorage.removeItem('accessToken')
    sessionStorage.removeItem('refreshToken')

    // 重置狀態
    user.value = null
    accessToken.value = null
    refreshToken.value = null
  }

  const refreshAccessToken = async (): Promise<string> => {
    try {
      const token = localStorage.getItem('refreshToken') || sessionStorage.getItem('refreshToken')

      if (!token) {
        throw new Error('No refresh token available')
      }

      const response = await api.post('/api/v1/auth/refresh', {
        refresh_token: token
      })

      const newAccessToken = response.data.access_token

      // 更新狀態
      accessToken.value = newAccessToken

      // 更新 storage（保持原有的儲存位置）
      if (localStorage.getItem('refreshToken')) {
        localStorage.setItem('accessToken', newAccessToken)
      } else {
        sessionStorage.setItem('accessToken', newAccessToken)
      }

      return newAccessToken
    } catch (error: any) {
      logout()
      return Promise.reject(error)
    }
  }

  const getCurrentUser = async (): Promise<void> => {
    try {
      const response = await api.get<User>('/api/v1/auth/me')
      user.value = response.data
    } catch (error: any) {
      // 不在這裡自動登出，讓調用方決定
      // 如果是 401，API 攔截器會處理 token 刷新
      return Promise.reject(error)
    }
  }

  // 初始化：從 storage 恢復狀態
  const initAuth = async (): Promise<void> => {
    // 如果已經在初始化，返回現有的 Promise
    if (initPromise) {
      return initPromise
    }

    initPromise = (async () => {
      console.log('[Auth] 開始初始化認證狀態...')

      const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken')
      const refresh = localStorage.getItem('refreshToken') || sessionStorage.getItem('refreshToken')

      if (token) {
        console.log('[Auth] 從 storage 恢復 token')
        accessToken.value = token
        refreshToken.value = refresh

        // 嘗試取得使用者資訊
        try {
          console.log('[Auth] 獲取使用者資訊...')
          await getCurrentUser()
          console.log('[Auth] 使用者資訊獲取成功:', user.value?.username)
        } catch (error: any) {
          console.warn('[Auth] 初始化時獲取使用者資訊失敗:', error.message)

          // 檢查錯誤類型
          if (error.response) {
            const status = error.response.status
            console.log('[Auth] API 錯誤狀態碼:', status)

            // 401/403 表示 token 完全無效（refresh 也失敗了）
            if (status === 401 || status === 403) {
              console.log('[Auth] Token 無效，清除認證狀態')
              logout()
            } else {
              // 其他 HTTP 錯誤（如 500）
              console.warn('[Auth] 伺服器錯誤，保留 token 等待重試')
            }
          } else if (error.request) {
            // 網絡錯誤（無法連接到伺服器）
            console.warn('[Auth] 網絡錯誤，保留 token')
            // 保留 token 和 accessToken.value
            // 但 user.value 保持為 null
            // isAuthenticated 仍會是 true（因為有 token）
          } else {
            // 其他錯誤
            console.warn('[Auth] 未知錯誤，保留 token')
          }
        }
      } else {
        console.log('[Auth] 沒有找到已儲存的 token')
      }

      // 標記初始化完成
      isInitialized.value = true
      console.log('[Auth] 初始化完成，isAuthenticated:', isAuthenticated.value)
    })()

    return initPromise
  }

  // 等待初始化完成的輔助方法
  const waitForInit = async (): Promise<void> => {
    if (isInitialized.value) {
      return Promise.resolve()
    }
    if (initPromise) {
      return initPromise
    }
    // 如果還沒開始初始化，開始初始化
    return initAuth()
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isInitialized,
    // Computed
    isAuthenticated,
    // Actions
    register,
    login,
    logout,
    refreshAccessToken,
    getCurrentUser,
    initAuth,
    waitForInit  // 導出等待方法
  }
})

