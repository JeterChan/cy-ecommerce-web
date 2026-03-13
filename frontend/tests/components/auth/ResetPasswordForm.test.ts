import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ResetPasswordForm from '@/components/auth/ResetPasswordForm.vue'
import { authService } from '@/services/authService'
import { createI18n } from 'vue-i18n'

// Mock dependencies
vi.mock('@/services/authService', () => ({
  authService: {
    resetPassword: vi.fn(),
  }
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

const i18n = createI18n({
  legacy: false,
  locale: 'zh-TW',
  messages: {
    'zh-TW': {
      'resetPassword.newPassword': '新密碼',
      'resetPassword.confirmNewPassword': '確認新密碼',
      'resetPassword.submit': '重設密碼',
      'resetPassword.success': '密碼重設成功',
      'validation.required': '此欄位為必填',
    }
  }
})

describe('ResetPasswordForm.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders correctly', () => {
    const wrapper = mount(ResetPasswordForm, {
      props: { token: 'valid-token' },
      global: { plugins: [i18n] }
    })
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('calls authService.resetPassword with correct data when form is valid', async () => {
    const wrapper = mount(ResetPasswordForm, {
      props: { token: 'test-token' },
      global: { plugins: [i18n] }
    })
    
    vi.mocked(authService.resetPassword).mockResolvedValueOnce(undefined)

    // Simulate input
    const inputs = wrapper.findAll('input[type="password"]')
    await inputs[0].setValue('Password123!')
    await inputs[1].setValue('Password123!')
    
    // Submit form
    await wrapper.find('form').trigger('submit')
    
    // Wait for form submission (vee-validate async)
    await new Promise(r => setTimeout(r, 0))

    expect(authService.resetPassword).toHaveBeenCalledWith('test-token', {
      password: 'Password123!',
    })
    expect(wrapper.text()).toContain('密碼重設成功')
  })

  it('shows error message if API fails', async () => {
    const wrapper = mount(ResetPasswordForm, {
      props: { token: 'test-token' },
      global: { plugins: [i18n] }
    })
    
    vi.mocked(authService.resetPassword).mockRejectedValueOnce(new Error('Invalid token'))

    const inputs = wrapper.findAll('input[type="password"]')
    await inputs[0].setValue('Password123!')
    await inputs[1].setValue('Password123!')
    
    await wrapper.find('form').trigger('submit')
    await new Promise(r => setTimeout(r, 0))

    expect(wrapper.text()).toContain('Invalid token')
  })
})
