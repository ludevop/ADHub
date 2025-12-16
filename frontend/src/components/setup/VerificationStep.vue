<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useSetupStore } from '@/stores/setup'
import type { VerificationTest } from '@/types/setup'
import { setupApi } from '@/api/setup'

const setupStore = useSetupStore()
const running = ref(false)
const needsPassword = ref(false)
const adminPassword = ref('')
const passwordError = ref('')

const testsByCategory = computed(() => {
  if (!setupStore.verificationResults) return {}

  const categories: Record<string, VerificationTest[]> = {}

  setupStore.verificationResults.tests.forEach((test) => {
    if (!categories[test.category]) {
      categories[test.category] = []
    }
    categories[test.category].push(test)
  })

  return categories
})

const categoryNames: Record<string, string> = {
  prerequisites: '📋 Prerequisites',
  dns: '🌍 DNS Services',
  services: '⚙️ Service Ports',
  ldap: '📂 LDAP Functionality',
  kerberos: '🔐 Kerberos Authentication',
  authentication: '✅ User Authentication'
}

onMounted(async () => {
  console.log('VerificationStep mounted')
  console.log('Current isProvisioned:', setupStore.isProvisioned)
  console.log('Current domain config:', {
    realm: setupStore.domainConfig.realm,
    domain_name: setupStore.domainConfig.domain_name,
    domain: setupStore.domainConfig.domain
  })

  // Refresh status to ensure it's up to date
  await setupStore.checkStatus()
  console.log('After status check, isProvisioned:', setupStore.isProvisioned)

  await checkAndPrepareConfig()

  if (!setupStore.verificationResults && !needsPassword.value) {
    await runTests()
  }
})

async function checkAndPrepareConfig() {
  // If domain is provisioned, we need to populate config from existing domain
  if (setupStore.isProvisioned) {
    try {
      // Always fetch domain info when domain is provisioned
      // Check if we need to fetch (if still using default values)
      const needsFetch =
        setupStore.domainConfig.domain_name === 'example.com' ||
        setupStore.domainConfig.realm === 'EXAMPLE.COM'

      if (needsFetch) {
        console.log('Fetching domain info...')
        // Get domain info to populate realm and domain_name
        const domainInfo = await setupApi.getDomainInfo()
        console.log('Domain info received:', domainInfo)

        // Extract realm and domain name from domain info
        // samba-tool domain info returns: Forest, Domain, Netbios domain
        if (domainInfo.Forest) {
          setupStore.domainConfig.realm = domainInfo.Forest.toUpperCase()
          setupStore.domainConfig.domain_name = domainInfo.Forest.toLowerCase()
          console.log('Set realm to:', setupStore.domainConfig.realm)
          console.log('Set domain_name to:', setupStore.domainConfig.domain_name)
        }
        if (domainInfo.Domain) {
          setupStore.domainConfig.domain_name = domainInfo.Domain.toLowerCase()
          console.log('Updated domain_name to:', setupStore.domainConfig.domain_name)
        }
        if (domainInfo['Netbios domain']) {
          setupStore.domainConfig.domain = domainInfo['Netbios domain'].toUpperCase()
          console.log('Set domain to:', setupStore.domainConfig.domain)
        }

        // Set other required fields for tests
        setupStore.domainConfig.dns_backend = 'SAMBA_INTERNAL'
        setupStore.domainConfig.server_role = 'dc'
      } else {
        console.log('Config already populated, skipping fetch')
      }

      // Check if we need password
      if (setupStore.domainConfig.admin_password.length < 8) {
        needsPassword.value = true
      } else {
        needsPassword.value = false
      }
    } catch (error) {
      console.error('Failed to get domain info:', error)
      passwordError.value = `Failed to load domain info: ${error instanceof Error ? error.message : 'Unknown error'}`
      needsPassword.value = true
    }
  } else {
    console.log('Domain not provisioned')
    // Not provisioned, check if we have password
    if (setupStore.domainConfig.admin_password.length < 8) {
      needsPassword.value = true
    } else {
      needsPassword.value = false
    }
  }
}

async function submitPassword() {
  passwordError.value = ''

  if (adminPassword.value.length < 8) {
    passwordError.value = 'Password must be at least 8 characters'
    return
  }

  // Set the password in the config
  setupStore.domainConfig.admin_password = adminPassword.value
  needsPassword.value = false

  // Run tests automatically after password is provided
  await runTests()
}

async function runTests() {
  // Always check and prepare config before running tests
  await checkAndPrepareConfig()

  // Check if we need password first
  if (!setupStore.domainConfig.admin_password || setupStore.domainConfig.admin_password.length < 8) {
    needsPassword.value = true
    passwordError.value = 'Administrator password is required for verification tests'
    return
  }

  // Check if config is properly populated
  if (
    setupStore.domainConfig.domain_name === 'example.com' ||
    setupStore.domainConfig.realm === 'EXAMPLE.COM'
  ) {
    passwordError.value = 'Unable to load domain configuration. Please check if domain is provisioned.'
    return
  }

  running.value = true
  try {
    await setupStore.runVerificationTests()
  } catch (error) {
    console.error('Verification tests failed:', error)
  } finally {
    running.value = false
  }
}

function getStatusClass(status: string) {
  return {
    'status-passed': status === 'passed',
    'status-failed': status === 'failed',
    'status-skipped': status === 'skipped',
    'status-running': status === 'running'
  }
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'passed':
      return '✓'
    case 'failed':
      return '✗'
    case 'skipped':
      return '⊘'
    case 'running':
      return '⟳'
    default:
      return '?'
  }
}
</script>

<template>
  <div class="verification-step">
    <h2>Verification Tests</h2>
    <p class="description">
      Running comprehensive tests to ensure everything is working correctly.
    </p>

    <!-- Password input form for existing domain -->
    <div v-if="needsPassword" class="password-form">
      <div class="info-box">
        <h3>🔑 Administrator Password Required</h3>
        <p>
          To run Kerberos and authentication tests on the existing domain, please enter the
          administrator password.
        </p>
        <p class="note">This password is only used for verification tests and is not stored.</p>
      </div>

      <form @submit.prevent="submitPassword" class="form">
        <div class="form-group">
          <label for="admin-password">Administrator Password</label>
          <input
            id="admin-password"
            v-model="adminPassword"
            type="password"
            placeholder="Enter administrator password"
            class="password-input"
            autocomplete="current-password"
          />
          <small v-if="passwordError" class="error-text">{{ passwordError }}</small>
        </div>

        <button type="submit" class="btn btn-primary" :disabled="adminPassword.length < 8">
          Run Verification Tests →
        </button>
      </form>
    </div>

    <div v-else-if="running" class="loading">
      <div class="spinner"></div>
      <p>Running verification tests...</p>
      <p class="sub-text">This may take a minute or two</p>
    </div>

    <div v-else-if="setupStore.verificationResults" class="results-container">
      <!-- Summary -->
      <div
        :class="[
          'summary-box',
          setupStore.verificationResults.overall_status === 'passed'
            ? 'summary-success'
            : setupStore.verificationResults.overall_status === 'partial'
              ? 'summary-warning'
              : 'summary-error'
        ]"
      >
        <h3>
          {{
            setupStore.verificationResults.overall_status === 'passed'
              ? '✅ All Tests Passed!'
              : setupStore.verificationResults.overall_status === 'partial'
                ? '⚠️ Some Tests Failed'
                : '❌ Tests Failed'
          }}
        </h3>
        <p>{{ setupStore.verificationResults.summary }}</p>

        <div class="summary-stats">
          <div class="stat">
            <span class="stat-number">{{ setupStore.verificationResults.total_tests }}</span>
            <span class="stat-label">Total</span>
          </div>
          <div class="stat stat-passed">
            <span class="stat-number">{{ setupStore.verificationResults.passed }}</span>
            <span class="stat-label">Passed</span>
          </div>
          <div class="stat stat-failed">
            <span class="stat-number">{{ setupStore.verificationResults.failed }}</span>
            <span class="stat-label">Failed</span>
          </div>
          <div class="stat stat-skipped">
            <span class="stat-number">{{ setupStore.verificationResults.skipped }}</span>
            <span class="stat-label">Skipped</span>
          </div>
        </div>
      </div>

      <!-- Tests by category -->
      <div class="categories-container">
        <div v-for="(tests, category) in testsByCategory" :key="category" class="category-section">
          <h3 class="category-title">
            {{ categoryNames[category] || category }}
          </h3>

          <div class="tests-list">
            <div v-for="test in tests" :key="test.test_name" class="test-item">
              <div class="test-header">
                <span class="test-icon" :class="getStatusClass(test.status)">
                  {{ getStatusIcon(test.status) }}
                </span>
                <span class="test-name">{{ test.test_name }}</span>
                <span v-if="test.duration_ms" class="test-duration">
                  {{ test.duration_ms }}ms
                </span>
              </div>

              <div class="test-message" :class="getStatusClass(test.status)">
                {{ test.message }}
              </div>

              <div v-if="test.details" class="test-details">
                <details>
                  <summary>Details</summary>
                  <pre>{{ test.details }}</pre>
                </details>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="setupStore.verificationResults.failed > 0" class="failure-info">
        <h4>🔧 Troubleshooting</h4>
        <p>Some tests failed. This may be due to:</p>
        <ul>
          <li>Services still starting up (wait a few seconds and retry)</li>
          <li>Firewall blocking ports</li>
          <li>Missing system utilities (ldapsearch, smbclient, etc.)</li>
          <li>DNS configuration issues</li>
        </ul>
        <p>Check the test details above for specific errors.</p>
      </div>
    </div>

    <div class="button-group">
      <button @click="runTests" class="btn btn-secondary" :disabled="running">
        🔄 Run Tests Again
      </button>
      <button @click="setupStore.nextStep()" class="btn btn-primary" :disabled="running">
        {{
          setupStore.verificationResults?.overall_status === 'passed'
            ? 'Complete Setup →'
            : 'Continue Anyway →'
        }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.verification-step {
  display: grid;
  gap: 1.5rem;
}

h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.description {
  text-align: center;
  color: #7f8c8d;
}

.password-form {
  max-width: 600px;
  margin: 2rem auto;
}

.info-box {
  background: #e8f4f8;
  border-left: 4px solid #3498db;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.info-box h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.info-box p {
  margin: 0.5rem 0;
  color: #555;
}

.info-box .note {
  font-size: 0.9rem;
  color: #7f8c8d;
  font-style: italic;
}

.form {
  display: grid;
  gap: 1.5rem;
}

.form-group {
  display: grid;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
}

.password-input {
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.password-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.error-text {
  color: #e74c3c;
  font-size: 0.9rem;
}

.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  border: 6px solid #f3f3f3;
  border-top: 6px solid #3498db;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.sub-text {
  color: #999;
  font-size: 0.9rem;
}

.results-container {
  display: grid;
  gap: 2rem;
}

.summary-box {
  padding: 2rem;
  border-radius: 8px;
  border-left: 4px solid;
  text-align: center;
}

.summary-success {
  background: #d4edda;
  border-color: #2ecc71;
}

.summary-warning {
  background: #fff3cd;
  border-color: #f39c12;
}

.summary-error {
  background: #f8d7da;
  border-color: #e74c3c;
}

.summary-box h3 {
  margin-top: 0;
  margin-bottom: 1rem;
}

.summary-stats {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 1.5rem;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.stat-passed .stat-number {
  color: #2ecc71;
}

.stat-failed .stat-number {
  color: #e74c3c;
}

.stat-skipped .stat-number {
  color: #95a5a6;
}

.categories-container {
  display: grid;
  gap: 1.5rem;
}

.category-section {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
}

.category-title {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
  font-size: 1.2rem;
}

.tests-list {
  display: grid;
  gap: 1rem;
}

.test-item {
  border-left: 3px solid #e0e0e0;
  padding-left: 1rem;
}

.test-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.test-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.9rem;
}

.test-icon.status-passed {
  background: #2ecc71;
  color: white;
}

.test-icon.status-failed {
  background: #e74c3c;
  color: white;
}

.test-icon.status-skipped {
  background: #95a5a6;
  color: white;
}

.test-icon.status-running {
  background: #3498db;
  color: white;
  animation: spin 1s linear infinite;
}

.test-name {
  flex: 1;
  font-weight: 600;
  color: #2c3e50;
}

.test-duration {
  font-size: 0.85rem;
  color: #999;
  font-family: monospace;
}

.test-message {
  color: #555;
  font-size: 0.95rem;
}

.test-message.status-failed {
  color: #c33;
}

.test-details {
  margin-top: 0.5rem;
}

details {
  cursor: pointer;
}

details summary {
  color: #3498db;
  font-size: 0.9rem;
}

details pre {
  margin-top: 0.5rem;
  background: #f8f9fa;
  padding: 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  overflow-x: auto;
}

.failure-info {
  background: #fff3cd;
  border-left: 4px solid #f39c12;
  padding: 1.5rem;
  border-radius: 8px;
}

.failure-info h4 {
  margin-top: 0;
  margin-bottom: 1rem;
}

.failure-info ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.failure-info li {
  margin: 0.5rem 0;
}

.button-group {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
}
</style>
