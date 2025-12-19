// DNS management API client

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

export interface DNSZone {
  name: string
  type: string
}

export interface DNSRecord {
  zone: string
  name: string
  type: string
  data: string
}

export interface DNSRecordCreate {
  zone: string
  name: string
  type: string
  data: string
  admin_password: string
}

export interface DNSRecordDelete {
  zone: string
  name: string
  type: string
  data: string
  admin_password: string
}

export interface DNSZoneListResponse {
  zones: DNSZone[]
  total: number
}

export interface DNSRecordListResponse {
  records: DNSRecord[]
  total: number
  zone: string
}

export const dnsApi = {
  async listZones(): Promise<DNSZoneListResponse> {
    const response = await api.get<DNSZoneListResponse>('/dns/zones')
    return response.data
  },

  async listRecords(zone: string): Promise<DNSRecordListResponse> {
    const response = await api.get<DNSRecordListResponse>(`/dns/zones/${zone}/records`)
    return response.data
  },

  async addRecord(recordData: DNSRecordCreate): Promise<DNSRecord> {
    const response = await api.post<DNSRecord>('/dns/records', recordData)
    return response.data
  },

  async deleteRecord(recordData: DNSRecordDelete): Promise<void> {
    await api.delete('/dns/records', { data: recordData })
  }
}
