import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/lib/api'
import type { User, LoginResponse, RegisterResponse } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => {
    return !!(accessToken.value && user.value)
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
      const response = await api.get<User>('/api/v1/auth/users/me')
      user.value = response.data
    } catch (error: any) {
      // 如果取得使用者失敗，清除狀態
      logout()
      return Promise.reject(error)
    }
  }

  // 初始化：從 storage 恢復狀態
  const initAuth = async (): Promise<void> => {
    const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken')
    const refresh = localStorage.getItem('refreshToken') || sessionStorage.getItem('refreshToken')

    if (token) {
      accessToken.value = token
      refreshToken.value = refresh

      // 嘗試取得使用者資訊
      try {
        await getCurrentUser()
      } catch (error) {
        // 如果取得失敗，清除狀態
        logout()
      }
    }
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    // Computed
    isAuthenticated,
    // Actions
    register,
    login,
    logout,
    refreshAccessToken,
    getCurrentUser,
    initAuth
  }
})

