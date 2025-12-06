import { ref } from 'vue'
import { ShippingMethod, type PurchaserInfo, type ShippingInfo } from '@/types/orderInfo'

export function useCheckoutValidation() {
  const errors = ref<Record<string, string>>({})

  const validatePurchaser = (info: PurchaserInfo): boolean => {
    const newErrors: Record<string, string> = {}
    let isValid = true

    if (!info.name?.trim()) {
      newErrors.name = '請輸入姓名'
      isValid = false
    }

    if (!info.phone?.trim()) {
      newErrors.phone = '請輸入電話'
      isValid = false
    } else if (!/^09\d{8}$/.test(info.phone)) {
      newErrors.phone = '請輸入有效的手機號碼 (09xxxxxxxx)'
      isValid = false
    }

    if (!info.email?.trim()) {
      newErrors.email = '請輸入 Email'
      isValid = false
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(info.email)) {
      newErrors.email = '請輸入有效的 Email 格式'
      isValid = false
    }

    // Merge errors into main errors object (clearing previous purchaser errors first effectively)
    // For simplicity, we just assign to keys directly, assuming no collision with shipping keys if managed separately
    // But since we want one errors object, we can key them specifically if needed or just mix them.
    // Let's assume the component consuming this maps them correctly.
    // Actually, let's keep purchaser errors separate in usage, or prefix them?
    // The forms use direct keys "name", "phone". Shipping uses "recipient_name".
    // So keys don't collide except maybe "phone" if we weren't careful, but Purchaser uses "phone", Shipping "recipient_phone".
    Object.assign(errors.value, newErrors)
    
    // Clear valid fields
    if (info.name?.trim()) delete errors.value.name
    if (info.phone?.trim() && /^09\d{8}$/.test(info.phone)) delete errors.value.phone
    if (info.email?.trim() && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(info.email)) delete errors.value.email

    return isValid
  }

  const validateShipping = (info: ShippingInfo): boolean => {
    const newErrors: Record<string, string> = {}
    let isValid = true

    if (!info.recipient_name?.trim()) {
      newErrors.recipient_name = '請輸入收件人姓名'
      isValid = false
    }

    if (!info.recipient_phone?.trim()) {
      newErrors.recipient_phone = '請輸入收件人電話'
      isValid = false
    } else if (!/^09\d{8}$/.test(info.recipient_phone)) {
      newErrors.recipient_phone = '請輸入有效的手機號碼'
      isValid = false
    }

    if (info.method === ShippingMethod.HOME_DELIVERY) {
      if (!info.address?.trim()) {
        newErrors.address = '請輸入收件地址'
        isValid = false
      }
    } else if (info.method === ShippingMethod.STORE_PICKUP_711) {
      if (!info.store_name?.trim()) {
        newErrors.store_name = '請輸入門市名稱'
        isValid = false
      }
    }

    Object.assign(errors.value, newErrors)
    
    // Clear valid fields
    if (info.recipient_name?.trim()) delete errors.value.recipient_name
    if (info.recipient_phone?.trim() && /^09\d{8}$/.test(info.recipient_phone)) delete errors.value.recipient_phone
    if (info.method === ShippingMethod.HOME_DELIVERY && info.address?.trim()) delete errors.value.address
    if (info.method === ShippingMethod.STORE_PICKUP_711 && info.store_name?.trim()) delete errors.value.store_name

    return isValid
  }

  const clearErrors = () => {
    errors.value = {}
  }

  return {
    errors,
    validatePurchaser,
    validateShipping,
    clearErrors
  }
}
