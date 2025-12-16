// Setup API client

import axios from 'axios'
import type {
  DomainConfig,
  PrerequisitesResponse,
  ProvisionResponse,
  VerificationResponse,
  SetupStatusResponse
} from '@/types/setup'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

export const setupApi = {
  // Get setup status
  async getStatus(): Promise<SetupStatusResponse> {
    const response = await api.get<SetupStatusResponse>('/setup/status')
    return response.data
  },

  // Check prerequisites
  async checkPrerequisites(): Promise<PrerequisitesResponse> {
    const response = await api.post<PrerequisitesResponse>('/setup/check-prerequisites')
    return response.data
  },

  // Validate configuration
  async validateConfig(config: DomainConfig): Promise<any> {
    const response = await api.post('/setup/validate-config', config)
    return response.data
  },

  // Provision domain
  async provisionDomain(config: DomainConfig): Promise<ProvisionResponse> {
    const response = await api.post<ProvisionResponse>('/setup/provision', config)
    return response.data
  },

  // Run verification tests
  async verifyInstallation(config: DomainConfig): Promise<VerificationResponse> {
    const response = await api.post<VerificationResponse>('/setup/verify', config)
    return response.data
  },

  // Get domain info
  async getDomainInfo(): Promise<Record<string, string>> {
    const response = await api.get('/setup/domain-info')
    return response.data
  },

  // Reset domain configuration
  async resetDomain(): Promise<{ success: boolean; message: string }> {
    const response = await api.post('/setup/reset')
    return response.data
  }
}
