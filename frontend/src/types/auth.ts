// Authentication types

export interface LoginRequest {
  username: string
  password: string
  remember_me?: boolean
}

export interface Token {
  access_token: string
  token_type: string
  expires_in: number
}

export interface User {
  username: string
  display_name?: string
  email?: string
  domain: string
  groups: string[]
  is_admin: boolean
}

export interface SetupStatus {
  is_completed: boolean
  completed_at?: string
  can_skip_to_dashboard: boolean
}
