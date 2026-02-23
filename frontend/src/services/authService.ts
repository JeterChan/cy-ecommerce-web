import api from '@/lib/api'
import type { User, ProfileUpdateRequest } from '@/types/auth'

export const authService = {
  /**
   * 更新當前使用者的個人檔案
   */
  async updateProfile(data: ProfileUpdateRequest): Promise<User> {
    const response = await api.patch<User>('/api/v1/auth/me', data)
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

