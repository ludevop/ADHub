// Setup wizard store

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  DomainConfig,
  PrerequisitesResponse,
  ProvisionResponse,
  VerificationResponse,
  SetupStatusResponse,
  SetupStep,
  DNSBackendType,
  DomainFunctionLevel
} from '@/types/setup'
import { setupApi } from '@/api/setup'

export const useSetupStore = defineStore('setup', () => {
  // State
  const currentStep = ref<SetupStep>(0)
  const setupStatus = ref<SetupStatusResponse | null>(null)
  const prerequisites = ref<PrerequisitesResponse | null>(null)
  const verificationResults = ref<VerificationResponse | null>(null)
  const provisionResponse = ref<ProvisionResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Domain configuration
  const domainConfig = ref<DomainConfig>({
    realm: 'EXAMPLE.COM',
    domain: 'EXAMPLE',
    domain_name: 'example.com',
    admin_password: '',
    dns_backend: 'SAMBA_INTERNAL' as DNSBackendType,
    dns_forwarder: '8.8.8.8',
    server_role: 'dc',
    function_level: '2008' as DomainFunctionLevel
  })

  // Computed
  const isProvisioned = computed(() => setupStatus.value?.is_provisioned ?? false)
  const canProceed = computed(() => {
    if (currentStep.value === 1) {
      // Prerequisites step
      return prerequisites.value?.all_passed ?? false
    }
    return true
  })

  // Actions
  async function checkStatus() {
    loading.value = true
    error.value = null
    try {
      setupStatus.value = await setupApi.getStatus()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to check status'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function checkPrerequisites() {
    loading.value = true
    error.value = null
    try {
      prerequisites.value = await setupApi.checkPrerequisites()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to check prerequisites'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function validateConfiguration() {
    loading.value = true
    error.value = null
    try {
      const result = await setupApi.validateConfig(domainConfig.value)
      return result
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Configuration validation failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function provisionDomain() {
    loading.value = true
    error.value = null
    try {
      provisionResponse.value = await setupApi.provisionDomain(domainConfig.value)
      return provisionResponse.value
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Domain provisioning failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function runVerificationTests() {
    loading.value = true
    error.value = null
    try {
      verificationResults.value = await setupApi.verifyInstallation(domainConfig.value)
      return verificationResults.value
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Verification tests failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  function nextStep() {
    if (currentStep.value < 7) {
      currentStep.value++
    }
  }

  function previousStep() {
    if (currentStep.value > 0) {
      currentStep.value--
    }
  }

  function goToStep(step: SetupStep) {
    currentStep.value = step
  }

  function resetWizard() {
    currentStep.value = 0
    prerequisites.value = null
    verificationResults.value = null
    provisionResponse.value = null
    error.value = null
  }

  async function resetDomain() {
    loading.value = true
    error.value = null
    try {
      const result = await setupApi.resetDomain()
      // Refresh status after reset
      await checkStatus()
      // Reset wizard to beginning
      resetWizard()
      return result
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Domain reset failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  function skipToVerification() {
    // Jump directly to verification step (step 6)
    currentStep.value = 6
  }

  return {
    // State
    currentStep,
    setupStatus,
    prerequisites,
    verificationResults,
    provisionResponse,
    domainConfig,
    loading,
    error,

    // Computed
    isProvisioned,
    canProceed,

    // Actions
    checkStatus,
    checkPrerequisites,
    validateConfiguration,
    provisionDomain,
    runVerificationTests,
    nextStep,
    previousStep,
    goToStep,
    resetWizard,
    resetDomain,
    skipToVerification
  }
})
