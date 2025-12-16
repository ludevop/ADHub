<script setup lang="ts">
import { ref } from 'vue'
import { useSetupStore } from '@/stores/setup'

const setupStore = useSetupStore()
const emit = defineEmits(['close'])

const resetting = ref(false)
const errorMessage = ref<string | null>(null)

async function handleSkip() {
  setupStore.skipToVerification()
  emit('close')
}

async function handleReset() {
  resetting.value = true
  errorMessage.value = null

  try {
    await setupStore.resetDomain()
    emit('close')
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to reset domain'
  } finally {
    resetting.value = false
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>⚠️ Existing Domain Detected</h2>
      </div>

      <div class="modal-body">
        <p class="info-text">
          A Samba Active Directory domain is already configured on this system.
        </p>

        <div v-if="setupStore.setupStatus?.domain_info" class="domain-details">
          <h3>Domain Information:</h3>
          <div class="info-grid">
            <div v-for="(value, key) in setupStore.setupStatus.domain_info" :key="key" class="info-item">
              <strong>{{ key }}:</strong>
              <span>{{ value }}</span>
            </div>
          </div>
        </div>

        <div class="options-section">
          <h3>What would you like to do?</h3>

          <div class="option-card">
            <div class="option-icon">✓</div>
            <div class="option-content">
              <h4>Continue to Verification</h4>
              <p>Skip the setup steps and go directly to verification tests to check if the existing domain is working correctly.</p>
              <button @click="handleSkip" class="btn btn-primary" :disabled="resetting">
                Continue to Verification →
              </button>
            </div>
          </div>

          <div class="option-card danger">
            <div class="option-icon">🗑️</div>
            <div class="option-content">
              <h4>Reset and Start Fresh</h4>
              <p class="warning-text">
                <strong>⚠️ Warning:</strong> This will permanently delete the existing domain configuration
                and all associated data. A backup will be created before deletion.
              </p>
              <button @click="handleReset" class="btn btn-danger" :disabled="resetting">
                {{ resetting ? 'Resetting...' : 'Reset Domain and Restart Setup' }}
              </button>
            </div>
          </div>
        </div>

        <div v-if="errorMessage" class="error-message">
          <strong>Error:</strong> {{ errorMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 2px solid #e0e0e0;
}

.modal-header h2 {
  margin: 0;
  color: #e67e22;
  font-size: 1.75rem;
}

.modal-body {
  padding: 2rem;
}

.info-text {
  font-size: 1.1rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.domain-details {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.domain-details h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
  font-size: 1rem;
}

.info-grid {
  display: grid;
  gap: 0.5rem;
}

.info-item {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.info-item strong {
  color: #7f8c8d;
}

.options-section {
  margin-top: 2rem;
}

.options-section h3 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.option-card {
  display: grid;
  grid-template-columns: 60px 1fr;
  gap: 1rem;
  padding: 1.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 1rem;
  transition: all 0.2s;
}

.option-card:hover {
  border-color: #3498db;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.1);
}

.option-card.danger:hover {
  border-color: #e74c3c;
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.1);
}

.option-icon {
  font-size: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.option-content h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.option-content p {
  color: #7f8c8d;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.warning-text {
  color: #c0392b !important;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
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
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c0392b;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.error-message {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #fee;
  border-left: 4px solid #e74c3c;
  border-radius: 4px;
  color: #c0392b;
}

@media (max-width: 768px) {
  .option-card {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .option-icon {
    margin-bottom: 0.5rem;
  }

  .info-item {
    grid-template-columns: 1fr;
  }
}
</style>
