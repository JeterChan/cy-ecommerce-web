import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import VerifyEmailView from '@/views/auth/VerifyEmailView.vue'
import { authService } from '@/services/authService'
import { createI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'

// Mock dependencies
vi.mock('@/services/authService', () => ({
  authService: {
    verifyEmail: vi.fn(),
  }
}))

vi.mock('vue-router', () => ({
  useRoute: vi.fn(),
  useRouter: vi.fn(),
}))

const i18n = createI18n({
  legacy: false,
  locale: 'zh-TW',
  messages: {
    'zh-TW': {
      'verifyEmail.title': '電子郵件驗證',
      'verifyEmail.verifying': '正在驗證您的電子郵件...',
      'verifyEmail.success': '電子郵件驗證成功！',
      'verifyEmail.failed': '驗證失敗，連結可能已過期或無效。',
      'auth.loginNow': '立即登入',
      'auth.backToLogin': '返回登入',
    }
  }
})

describe('VerifyEmailView.vue', () => {
  let mockPush: ReturnType<typeof vi.fn>

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush = vi.fn()
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any)
  })

  it('shows failed state when no token is provided', async () => {
    vi.mocked(useRoute).mockReturnValue({ query: {} } as any)
    
    const wrapper = mount(VerifyEmailView, {
      global: { 
        plugins: [i18n],
        stubs: ['router-link']
      }
    })
    
    // Wait for onMounted
    await new Promise(r => setTimeout(r, 0))

    expect(wrapper.text()).toContain('驗證失敗')
    expect(authService.verifyEmail).not.toHaveBeenCalled()
  })

  it('calls authService and shows success state for valid token', async () => {
    vi.mocked(useRoute).mockReturnValue({ query: { token: 'valid-token' } } as any)
    vi.mocked(authService.verifyEmail).mockResolvedValueOnce({ status: 'success', message: 'OK' })
    
    const wrapper = mount(VerifyEmailView, {
      global: { 
        plugins: [i18n],
        stubs: ['router-link']
      }
    })
    
    expect(wrapper.text()).toContain('正在驗證')
    
    await new Promise(r => setTimeout(r, 0))

    expect(authService.verifyEmail).toHaveBeenCalledWith('valid-token')
    expect(wrapper.text()).toContain('驗證成功')
  })

  it('shows error state when API fails', async () => {
    vi.mocked(useRoute).mockReturnValue({ query: { token: 'invalid-token' } })
    vi.mocked(authService.verifyEmail).mockRejectedValueOnce(new Error('verifyEmail.failed'))
    
    const wrapper = mount(VerifyEmailView, {
      global: { 
        plugins: [i18n],
        stubs: ['router-link']
      }
    })
    
    await new Promise(r => setTimeout(r, 0))

    expect(authService.verifyEmail).toHaveBeenCalledWith('invalid-token')
    expect(wrapper.text()).toContain('驗證失敗')
  })
})
