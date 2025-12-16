<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSetupStore } from '@/stores/setup'

const setupStore = useSetupStore()
const checking = ref(false)

onMounted(async () => {
  if (!setupStore.prerequisites) {
    await runChecks()
  }
})

async function runChecks() {
  checking.value = true
  try {
    await setupStore.checkPrerequisites()
  } catch (error) {
    console.error('Prerequisites check failed:', error)
  } finally {
    checking.value = false
  }
}

function getStatusClass(status: string) {
  return {
    'status-passed': status === 'passed',
    'status-warning': status === 'warning',
    'status-failed': status === 'failed'
  }
}
</script>

<template>
  <div class="prerequisites-step">
    <h2>System Prerequisites Check</h2>
    <p class="description">
      Verifying that your system meets all requirements for Samba AD DC installation.
    </p>

    <div v-if="checking" class="loading">
      <div class="spinner"></div>
      <p>Running system checks...</p>
    </div>

    <div v-else-if="setupStore.prerequisites" class="checks-container">
      <div
        v-for="check in setupStore.prerequisites.checks"
        :key="check.check_name"
        class="check-item"
      >
        <div class="check-header">
          <span class="check-icon" :class="getStatusClass(check.status)">
            {{ check.status === 'passed' ? '✓' : check.status === 'warning' ? '⚠' : '✗' }}
          </span>
          <span class="check-name">{{ check.check_name }}</span>
          <span class="check-status" :class="getStatusClass(check.status)">
            {{ check.status.toUpperCase() }}
          </span>
        </div>
        <div class="check-message">{{ check.message }}</div>
        <div v-if="check.details" class="check-details">{{ check.details }}</div>
      </div>

      <div v-if="!setupStore.prerequisites.all_passed" class="warning-box">
        <h3>⚠️ Action Required</h3>
        <p>
          Some prerequisites checks failed or returned warnings. Please resolve these issues before
          proceeding with the setup.
        </p>
      </div>

      <div v-else class="success-box">
        <h3>✅ All Checks Passed</h3>
        <p>Your system is ready for Samba AD DC provisioning!</p>
      </div>
    </div>

    <div class="button-group">
      <button @click="setupStore.previousStep()" class="btn btn-secondary">← Back</button>
      <button @click="runChecks" class="btn btn-secondary" :disabled="checking">
        🔄 Re-check
      </button>
      <button
        @click="setupStore.nextStep()"
        class="btn btn-primary"
        :disabled="!setupStore.canProceed || checking"
      >
        Continue →
      </button>
    </div>
  </div>
</template>

<style scoped>
.prerequisites-step {
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

.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.checks-container {
  display: grid;
  gap: 1rem;
}

.check-item {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 1rem;
}

.check-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.check-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.check-icon.status-passed {
  background: #2ecc71;
  color: white;
}

.check-icon.status-warning {
  background: #f39c12;
  color: white;
}

.check-icon.status-failed {
  background: #e74c3c;
  color: white;
}

.check-name {
  flex: 1;
  font-weight: 600;
}

.check-status {
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
}

.check-status.status-passed {
  background: #d4edda;
  color: #155724;
}

.check-status.status-warning {
  background: #fff3cd;
  color: #856404;
}

.check-status.status-failed {
  background: #f8d7da;
  color: #721c24;
}

.check-message {
  color: #555;
  margin-left: 46px;
}

.check-details {
  color: #888;
  font-size: 0.9rem;
  margin-left: 46px;
  margin-top: 0.25rem;
  font-family: monospace;
}

.warning-box,
.success-box {
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid;
}

.warning-box {
  background: #fff3cd;
  border-color: #f39c12;
}

.success-box {
  background: #d4edda;
  border-color: #2ecc71;
}

.warning-box h3,
.success-box h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
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
