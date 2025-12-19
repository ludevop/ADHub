// Share management API client

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

export interface Share {
  name: string
  path?: string | null
  comment?: string | null
  read_only: boolean
  guest_ok: boolean
  browseable: boolean
}

export interface ShareCreate {
  name: string
  path: string
  comment?: string
  read_only?: boolean
  guest_ok?: boolean
  browseable?: boolean
}

export interface ShareUpdate {
  path?: string | null
  comment?: string | null
  read_only?: boolean | null
  guest_ok?: boolean | null
  browseable?: boolean | null
}

export interface ShareListResponse {
  shares: Share[]
  total: number
}

export const sharesApi = {
  async listShares(): Promise<ShareListResponse> {
    const response = await api.get<ShareListResponse>('/shares')
    return response.data
  },

  async getShare(sharename: string): Promise<Share> {
    const response = await api.get<Share>(`/shares/${sharename}`)
    return response.data
  },

  async createShare(shareData: ShareCreate): Promise<Share> {
    const response = await api.post<Share>('/shares', shareData)
    return response.data
  },

  async updateShare(sharename: string, shareData: ShareUpdate): Promise<Share> {
    const response = await api.put<Share>(`/shares/${sharename}`, shareData)
    return response.data
  },

  async deleteShare(sharename: string): Promise<void> {
    await api.delete(`/shares/${sharename}`)
  }
}
