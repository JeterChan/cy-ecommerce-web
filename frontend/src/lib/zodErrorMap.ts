import { z } from 'zod'

/**
 * 自訂 Zod 錯誤訊息（正體中文）
 * 將 Zod 的預設英文錯誤訊息轉換為正體中文
 */
export const customZodErrorMap = ((issue: z.ZodIssueOptionalMessage, ctx: z.ErrorMapCtx) => {
  let message: string

  switch (issue.code) {
    case z.ZodIssueCode.invalid_type:
      if (issue.received === 'undefined') {
        message = '此欄位為必填'
      } else if (issue.expected === 'string') {
        message = '請輸入文字'
      } else if (issue.expected === 'number') {
        message = '請輸入數字'
      } else if (issue.expected === 'boolean') {
        message = '請選擇是或否'
      } else {
        message = `預期類型為 ${issue.expected}，但收到 ${issue.received}`
      }
      break

    case z.ZodIssueCode.invalid_string:
      message = '格式不正確'
      break

    case z.ZodIssueCode.too_small:
      if (issue.type === 'string') {
        if (issue.minimum === 1) {
          message = '此欄位不可為空'
        } else {
          message = `至少需要 ${issue.minimum} 個字元`
        }
      } else if (issue.type === 'number') {
        message = `數字不可小於 ${issue.minimum}`
      } else if (issue.type === 'array') {
        message = `至少需要 ${issue.minimum} 個項目`
      } else {
        message = '輸入過短'
      }
      break

    case z.ZodIssueCode.too_big:
      if (issue.type === 'string') {
        message = `不可超過 ${issue.maximum} 個字元`
      } else if (issue.type === 'number') {
        message = `數字不可大於 ${issue.maximum}`
      } else if (issue.type === 'array') {
        message = `不可超過 ${issue.maximum} 個項目`
      } else {
        message = '輸入過長'
      }
      break

    case z.ZodIssueCode.invalid_literal:
      message = '請選擇有效的選項'
      break

    case z.ZodIssueCode.unrecognized_keys:
      message = `發現無效的欄位：${issue.keys.join(', ')}`
      break

    case z.ZodIssueCode.custom:
      message = ctx.defaultError
      break

    default:
      message = ctx.defaultError
  }

  return { message }
}) satisfies z.ZodErrorMap

/**
 * Registers the custom Zod error map globally.
 *
 * Installs `customZodErrorMap` as Zod's global error map; call once during application initialization.
 */
export function setupZodErrorMap() {
  z.setErrorMap(customZodErrorMap)
}