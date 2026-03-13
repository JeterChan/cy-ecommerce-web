export interface User {
  id: string
  username: string
  email: string
  is_active: boolean
  created_at: string
  updated_at?: string
  // 個人檔案欄位
  phone?: string
  address?: string
  carrier_type?: string
  carrier_number?: string
  tax_id?: string
}

export interface ProfileUpdateRequest {
  username?: string
  phone?: string
  address?: string
  carrier_type?: string
  carrier_number?: string
  tax_id?: string
}

export interface EmailChangeRequest {
  new_email: string
  password: string
}

export interface LoginRequest {
  email: string
  password: string
  remember_me: boolean
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  refresh_token?: string
  user: User
}

export interface RegisterResponse {
  id: string
  username: string
  email: string
  is_active: boolean
  created_at: string
  updated_at?: string
}
