// Group management API client

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

export interface Group {
  name: string
  description?: string | null
  members: string[]
}

export interface GroupCreate {
  name: string
  description?: string
}

export interface GroupUpdate {
  description?: string | null
  admin_password: string
}

export interface GroupMemberOperation {
  username: string
}

export interface GroupListResponse {
  groups: Group[]
  total: number
}

export const groupsApi = {
  async listGroups(): Promise<GroupListResponse> {
    const response = await api.get<GroupListResponse>('/groups')
    return response.data
  },

  async getGroup(groupname: string): Promise<Group> {
    const response = await api.get<Group>(`/groups/${groupname}`)
    return response.data
  },

  async createGroup(groupData: GroupCreate): Promise<Group> {
    const response = await api.post<Group>('/groups', groupData)
    return response.data
  },

  async updateGroup(groupname: string, groupData: GroupUpdate): Promise<Group> {
    const response = await api.put<Group>(`/groups/${groupname}`, groupData)
    return response.data
  },

  async deleteGroup(groupname: string): Promise<void> {
    await api.delete(`/groups/${groupname}`)
  },

  async addMember(groupname: string, memberData: GroupMemberOperation): Promise<Group> {
    const response = await api.post<Group>(`/groups/${groupname}/members`, memberData)
    return response.data
  },

  async removeMember(groupname: string, username: string): Promise<Group> {
    const response = await api.delete<Group>(`/groups/${groupname}/members/${username}`)
    return response.data
  }
}
