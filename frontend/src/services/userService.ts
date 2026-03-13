import api from '@/lib/api'
import type { UserProfile } from '@/types/user'
import type { ProfileUpdateFormValues } from '@/models/auth.schema'

export const userService = {
  /**
   * 獲取使用者個人資料
   */
  async getProfile(): Promise<UserProfile> {
    try {
      const response = await api.get<UserProfile>('/api/v1/auth/me')
      return response.data
    } catch (error: any) {
      if (!error.response) {
        throw new Error('error.networkError')
      }
      if (error.response.status === 401) {
        throw new Error('error.unauthorized')
      }
      throw new Error(error.response.data?.message || 'error.generic')
    }
  },

  /**
   * 更新使用者個人資料
   */
  async updateProfile(data: ProfileUpdateFormValues): Promise<UserProfile> {
    try {
      const response = await api.patch<UserProfile>('/api/v1/auth/me/profile', data)
      return response.data
    } catch (error: any) {
      if (!error.response) {
        throw new Error('error.networkError')
      }
      if (error.response.status === 401) {
        throw new Error('error.unauthorized')
      }
      throw new Error(error.response.data?.message || 'error.generic')
    }
  },

  /**
   * 刪除帳號
   */
  async deleteAccount(): Promise<void> {
    try {
      await api.delete('/api/v1/users/me')
    } catch (error: any) {
      if (!error.response) {
        throw new Error('error.networkError')
      }
      if (error.response.status === 401) {
        throw new Error('error.unauthorized')
      }
      throw new Error(error.response.data?.message || 'error.generic')
    }
  }
}
