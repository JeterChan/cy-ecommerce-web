import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'

// 建立 Axios 實例
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 全域變數用於快取刷新 Token 的 Promise，避免競態條件
let refreshTokenPromise: Promise<string> | null = null

// 登出回調函數（由 main.ts 設定）
let onTokenExpired: (() => void) | null = null

/**
 * Registers a callback to be invoked when authentication tokens expire or are cleared.
 *
 * @param callback - Function called with no arguments when tokens are removed due to refresh failure or expiry
 */
export function setTokenExpiredCallback(callback: () => void) {
  onTokenExpired = callback
}

// Request 攔截器：自動注入 JWT Token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 優先從 localStorage 讀取，若無則從 sessionStorage
    const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken')

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response 攔截器：處理 401 錯誤與自動刷新 Token
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // 排除登入端點，登入失敗的 401 應由頁面自行處理
    if (originalRequest.url?.includes('/api/v1/auth/login')) {
      return Promise.reject(error)
    }

    // 處理 401 錯誤（Token 過期）
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      // 避免對 /auth/refresh 端點本身進行刷新
      if (originalRequest.url?.includes('/api/v1/auth/refresh')) {
        // Refresh Token 也過期了，清除所有 token 並登出
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        sessionStorage.removeItem('accessToken')
        sessionStorage.removeItem('refreshToken')

        // 呼叫登出回調（會在 main.ts 中設定）
        if (onTokenExpired) {
          onTokenExpired()
        }

        return Promise.reject(error)
      }

      originalRequest._retry = true

      try {
        // 使用 Promise 快取機制避免並發刷新
        if (!refreshTokenPromise) {
          const refreshToken = localStorage.getItem('refreshToken') || sessionStorage.getItem('refreshToken')

          if (!refreshToken) {
            throw new Error('No refresh token available')
          }

          refreshTokenPromise = api
            .post('/api/v1/auth/refresh', { refresh_token: refreshToken })
            .then((response) => {
              const newAccessToken = response.data.access_token

              // 更新 token（保持原有的儲存位置）
              if (localStorage.getItem('refreshToken')) {
                localStorage.setItem('accessToken', newAccessToken)
              } else {
                sessionStorage.setItem('accessToken', newAccessToken)
              }

              return newAccessToken
            })
            .finally(() => {
              refreshTokenPromise = null
            })
        }

        const newAccessToken = await refreshTokenPromise

        // 更新原請求的 Authorization header
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        }

        // 重試原請求
        return api.request(originalRequest)
      } catch (refreshError) {
        // Refresh 失敗，清除所有 token 並登出
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        sessionStorage.removeItem('accessToken')
        sessionStorage.removeItem('refreshToken')

        // 呼叫登出回調
        if (onTokenExpired) {
          onTokenExpired()
        }

        return Promise.reject(refreshError)
      }
    }

    // 不在攔截器中自動顯示錯誤 Toast
    // 讓各個頁面/組件自行處理錯誤訊息
    return Promise.reject(error)
  }
)

export default api
