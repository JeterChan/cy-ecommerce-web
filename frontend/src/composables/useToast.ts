import { ref } from 'vue'

export interface Toast {
  id: string
  title?: string
  description?: string
  variant?: 'default' | 'destructive'
  open: boolean
}

const toasts = ref<Toast[]>([])

let toastIdCounter = 0

export function useToast() {
  const showSuccess = (message: string, title?: string) => {
    const id = `toast-${++toastIdCounter}`
    toasts.value.push({
      id,
      title: title || '成功',
      description: message,
      variant: 'default',
      open: true
    })

    // 自動關閉 toast
    setTimeout(() => {
      const index = toasts.value.findIndex(t => t.id === id)
      if (index > -1 && toasts.value[index]) {
        toasts.value[index]!.open = false
        // 移除 toast
        setTimeout(() => {
          const removeIndex = toasts.value.findIndex(t => t.id === id)
          if (removeIndex > -1) {
            toasts.value.splice(removeIndex, 1)
          }
        }, 300)
      }
    }, 3000)
  }

  const showError = (message: string, title?: string) => {
    const id = `toast-${++toastIdCounter}`
    toasts.value.push({
      id,
      title: title || '錯誤',
      description: message,
      variant: 'destructive',
      open: true
    })

    // 自動關閉 toast
    setTimeout(() => {
      const index = toasts.value.findIndex(t => t.id === id)
      if (index > -1 && toasts.value[index]) {
        toasts.value[index]!.open = false
        // 移除 toast
        setTimeout(() => {
          const removeIndex = toasts.value.findIndex(t => t.id === id)
          if (removeIndex > -1) {
            toasts.value.splice(removeIndex, 1)
          }
        }, 300)
      }
    }, 3000)
  }

  return {
    toasts,
    showSuccess,
    showError
  }
}

