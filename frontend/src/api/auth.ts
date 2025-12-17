// Authentication API client

import axios from 'axios'
import type { LoginRequest, Token, User, SetupStatus } from '@/types/auth'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authApi = {
  // Login
  async login(credentials: LoginRequest): Promise<Token> {
    const response = await api.post<Token>('/auth/login', credentials)
    return response.data
  },

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  // Logout
  async logout(): Promise<void> {
    await api.post('/auth/logout')
  },

  // Get setup status
  async getSetupStatus(): Promise<SetupStatus> {
    const response = await api.get<SetupStatus>('/auth/setup-status')
    return response.data
  }
}
