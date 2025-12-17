// Authentication store

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginRequest, SetupStatus } from '@/types/auth'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const loading = ref(false)
  const error = ref<string | null>(null)
  const setupStatus = ref<SetupStatus | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_admin ?? false)
  const setupCompleted = computed(() => setupStatus.value?.is_completed ?? false)
  const canSkipToDashboard = computed(() => setupStatus.value?.can_skip_to_dashboard ?? false)

  // Actions
  async function login(credentials: LoginRequest) {
    loading.value = true
    error.value = null

    try {
      const tokenData = await authApi.login(credentials)

      // Store token
      token.value = tokenData.access_token
      localStorage.setItem('access_token', tokenData.access_token)

      // Fetch user info
      await fetchUser()

      return true
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Login failed'
      token.value = null
      user.value = null
      localStorage.removeItem('access_token')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) {
      user.value = null
      return
    }

    try {
      user.value = await authApi.getCurrentUser()
    } catch (e) {
      console.error('Failed to fetch user:', e)
      // Token might be invalid, clear it
      logout()
    }
  }

  async function checkSetupStatus() {
    try {
      setupStatus.value = await authApi.getSetupStatus()
    } catch (e) {
      console.error('Failed to fetch setup status:', e)
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (e) {
      console.error('Logout failed:', e)
    } finally {
      // Clear local state
      token.value = null
      user.value = null
      localStorage.removeItem('access_token')
    }
  }

  async function initialize() {
    // Check if we have a token
    if (token.value) {
      await fetchUser()
    }

    // Always check setup status
    await checkSetupStatus()
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    setupStatus,

    // Computed
    isAuthenticated,
    isAdmin,
    setupCompleted,
    canSkipToDashboard,

    // Actions
    login,
    logout,
    fetchUser,
    checkSetupStatus,
    initialize
  }
})
