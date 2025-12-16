<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSetupStore } from '@/stores/setup'
import { ProvisionStatus } from '@/types/setup'

const setupStore = useSetupStore()
const provisioning = ref(false)
const provisionStatus = ref<string>('')
const provisionOutput = ref<string[]>([])
const emit = defineEmits(['showExistingDomainModal'])

onMounted(async () => {
  // Check if domain already exists
  if (setupStore.isProvisioned) {
    provisionStatus.value = 'Domain already exists'
    return
  }

  await startProvisioning()
})

async function startProvisioning() {
  provisioning.value = true
  provisionStatus.value = 'Starting domain provision...'

  try {
    const response = await setupStore.provisionDomain()

    if (response.status === ProvisionStatus.COMPLETED) {
      provisionStatus.value = 'Provision completed successfully!'
      if (response.output) {
        provisionOutput.value = response.output.split('\n')
      }

      // Auto-advance to verification after 2 seconds
      setTimeout(() => {
        setupStore.nextStep()
      }, 2000)
    } else if (response.status === ProvisionStatus.FAILED) {
      provisionStatus.value = 'Provision failed'
      if (response.error) {
        provisionOutput.value = response.error.split('\n')
      }
    }
  } catch (error) {
    provisionStatus.value = 'Error during provisioning'
    provisionOutput.value = [error instanceof Error ? error.message : 'Unknown error']
  } finally {
    provisioning.value = false
  }
}
</script>

<template>
  <div class="provision-step">
    <h2>Provisioning Domain</h2>
    <p class="description">Setting up your Samba Active Directory domain controller...</p>

    <div class="provision-container">
      <!-- Domain already exists warning -->
      <div v-if="setupStore.isProvisioned && !provisioning" class="warning-box">
        <h3>⚠️ Domain Already Exists</h3>
        <p>A domain is already provisioned on this system. You must reset the existing configuration before creating a new domain.</p>
        <div class="action-buttons">
          <button @click="setupStore.skipToVerification()" class="btn btn-success">
            Skip to Verification →
          </button>
          <button @click="emit('showExistingDomainModal')" class="btn btn-warning">
            Reset Configuration
          </button>
        </div>
      </div>

      <div v-else-if="provisioning" class="loading-container">
        <div class="spinner"></div>
        <p class="status-message">{{ provisionStatus }}</p>
        <p class="sub-message">This may take several minutes. Please wait...</p>
      </div>

      <div v-else class="result-container">
        <div
          v-if="setupStore.provisionResponse?.status === ProvisionStatus.COMPLETED"
          class="success-box"
        >
          <h3>✅ Provision Successful!</h3>
          <p>Your Samba AD domain has been provisioned successfully.</p>
          <p class="next-info">Proceeding to verification tests...</p>
        </div>

        <div
          v-else-if="setupStore.provisionResponse?.status === ProvisionStatus.FAILED"
          class="error-box"
        >
          <h3>❌ Provision Failed</h3>
          <p>There was an error during domain provisioning. Please check the output below.</p>
        </div>

        <div v-if="provisionOutput.length > 0" class="output-container">
          <h4>Provision Output:</h4>
          <pre class="output">{{ provisionOutput.join('\n') }}</pre>
        </div>
      </div>
    </div>

    <div v-if="!provisioning" class="button-group">
      <button
        v-if="setupStore.provisionResponse?.status === ProvisionStatus.FAILED"
        @click="setupStore.previousStep()"
        class="btn btn-secondary"
      >
        ← Go Back
      </button>
      <button
        v-if="setupStore.provisionResponse?.status === ProvisionStatus.FAILED"
        @click="startProvisioning"
        class="btn btn-primary"
      >
        🔄 Retry
      </button>
      <button
        v-if="setupStore.provisionResponse?.status === ProvisionStatus.COMPLETED"
        @click="setupStore.nextStep()"
        class="btn btn-primary"
      >
        Continue to Verification →
      </button>
    </div>
  </div>
</template>

<style scoped>
.provision-step {
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

.provision-container {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-container {
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

.status-message {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.sub-message {
  color: #7f8c8d;
}

.result-container {
  width: 100%;
}

.success-box,
.error-box,
.warning-box {
  padding: 2rem;
  border-radius: 8px;
  border-left: 4px solid;
  margin-bottom: 1.5rem;
  text-align: center;
}

.success-box {
  background: #d4edda;
  border-color: #2ecc71;
}

.error-box {
  background: #f8d7da;
  border-color: #e74c3c;
}

.warning-box {
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  border: 2px solid #e67e22;
}

.warning-box h3 {
  color: #856404;
}

.warning-box p {
  color: #856404;
  margin-bottom: 1.5rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.success-box h3,
.error-box h3 {
  margin-top: 0;
  margin-bottom: 1rem;
}

.next-info {
  color: #155724;
  font-style: italic;
}

.output-container {
  margin-top: 1.5rem;
}

.output-container h4 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.output {
  background: #2c3e50;
  color: #ecf0f1;
  padding: 1rem;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  font-size: 0.9rem;
  white-space: pre-wrap;
  word-wrap: break-word;
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

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.btn-success {
  background: #2ecc71;
  color: white;
}

.btn-success:hover {
  background: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(46, 204, 113, 0.3);
}

.btn-warning {
  background: #e67e22;
  color: white;
}

.btn-warning:hover {
  background: #d35400;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(230, 126, 34, 0.3);
}
</style>
