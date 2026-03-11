export interface UserProfile {
  id: string;
  email: string;
  nickname: string;
  phone?: string;
  avatar_url?: string;
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
}

export interface AuthToken {
  token: string;
  type: 'RESET' | 'VERIFY';
}
