import * as z from 'zod'

export const ProductSchema = z.object({
  name: z.string().min(1, '請輸入商品名稱').max(100, '名稱不可超過 100 字元'),
  description: z.string().max(1000, '描述不可超過 1000 字元').optional(),
  price: z.number().positive('價格必須大於 0'),
  stock_quantity: z.number().int().min(0, '庫存不可為負數'),
  is_active: z.boolean().default(true),
  category_ids: z.array(z.number()).default([]),
  image_urls: z.array(z.string()).max(5, '最多上傳 5 張圖片')
})

export type ProductFormValues = z.infer<typeof ProductSchema>
