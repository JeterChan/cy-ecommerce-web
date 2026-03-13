import api from '@/lib/api'
import type { User, ProfileUpdateRequest, EmailChangeRequest } from '@/types/auth'

export const authService = {
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
    const response = await api.get<{ status: string; message: string }>('/api/v1/auth/me/email/verify', {
      params: { token, type, user_id: userId },
    })
    return response.data
  },

  /**
   * 獲取當前使用者資訊
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/v1/auth/me')
    return response.data
  },
}

