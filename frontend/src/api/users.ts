// User management API client

import axios from 'axios'

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

export interface User {
  username: string
  display_name?: string | null
  email?: string | null
  description?: string | null
  account_disabled: boolean
}

export interface UserCreate {
  username: string
  password: string
  given_name?: string
  surname?: string
  email?: string
  description?: string
  must_change_password?: boolean
}

export interface UserUpdate {
  display_name?: string | null
  email?: string | null
  description?: string | null
}

export interface UserPasswordChange {
  new_password: string
  must_change_at_next_login?: boolean
}

export interface UserListResponse {
  users: User[]
  total: number
}

export const usersApi = {
  async listUsers(): Promise<UserListResponse> {
    const response = await api.get<UserListResponse>('/users')
    return response.data
  },

  async getUser(username: string): Promise<User> {
    const response = await api.get<User>(`/users/${username}`)
    return response.data
  },

  async createUser(userData: UserCreate): Promise<User> {
    const response = await api.post<User>('/users', userData)
    return response.data
  },

  async updateUser(username: string, userData: UserUpdate): Promise<User> {
    const response = await api.put<User>(`/users/${username}`, userData)
    return response.data
  },

  async deleteUser(username: string): Promise<void> {
    await api.delete(`/users/${username}`)
  },

  async enableUser(username: string): Promise<User> {
    const response = await api.post<User>(`/users/${username}/enable`)
    return response.data
  },

  async disableUser(username: string): Promise<User> {
    const response = await api.post<User>(`/users/${username}/disable`)
    return response.data
  },

  async setPassword(username: string, passwordData: UserPasswordChange): Promise<void> {
    await api.post(`/users/${username}/password`, passwordData)
  }
}
