import api from '@/lib/api'
import type { User, ProfileUpdateRequest, EmailChangeRequest } from '@/types/auth'
import type { ForgotPasswordFormValues, ResetPasswordFormValues, ChangePasswordFormValues } from '@/models/auth.schema'

export const authService = {
  /**
   * 修改密碼 (登入狀態)
   */
  async changePassword(data: Omit<ChangePasswordFormValues, 'confirm_password'>): Promise<void> {
    try {
      await api.post('/api/v1/auth/me/change-password', data)
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'error.generic')
    }
  },

  /**
   * 忘記密碼 (請求發送重設信)
   */
  async forgotPassword(data: ForgotPasswordFormValues): Promise<void> {
    try {
      await api.post('/api/v1/auth/forgot-password', data)
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error('error.userNotRegistered')
      }
      throw new Error(error.response?.data?.detail || 'error.generic')
    }
  },

  /**
   * 重設密碼
   */
  async resetPassword(token: string, data: Omit<ResetPasswordFormValues, 'confirmPassword'>): Promise<void> {
    try {
      await api.post('/api/v1/auth/reset-password', { 
        token, 
        new_password: data.password 
      })
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'error.generic')
    }
  },

  /**
   * 驗證電子郵件 (新註冊)
   */
  async verifyEmail(token: string): Promise<{ status: string; message: string }> {
    try {
      const response = await api.get<{ status: string; message: string }>('/api/v1/auth/email-verify', {
        params: { token },
      })
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'error.generic')
    }
  },

  /**
   * 更新當前使用者的個人檔案
   */
  async updateProfile(data: ProfileUpdateRequest): Promise<User> {
    const response = await api.patch<User>('/api/v1/auth/me/profile', data)
    return response.data
  },

  /**
   * 請求變更電子郵件（寄送驗證信至舊/新信箱）
   */
  async requestEmailChange(data: EmailChangeRequest): Promise<void> {
    await api.post('/api/v1/auth/me/email/change', data)
  },

  /**
   * 驗證電子郵件變更 token（舊或新信箱）
   */
  async verifyEmailChange(token: string, type: string, userId: string): Promise<{ status: string; message: string }> {
    try {
      const response = await api.get<{ status: string; message: string }>('/api/v1/auth/me/email/verify', {
        params: { token, type, user_id: userId },
      })
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'error.generic')
    }
  },

  /**
   * 獲取當前使用者資訊
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/v1/auth/me')
    return response.data
  },
}

