<script setup lang="ts">
import { useSetupStore } from '@/stores/setup'

const setupStore = useSetupStore()
const config = setupStore.domainConfig
</script>

<template>
  <div class="review-step">
    <h2>Review Configuration</h2>
    <p class="description">Please review your settings before provisioning the domain.</p>

    <div class="review-container">
      <div class="review-section">
        <h3>🌐 Domain Settings</h3>
        <div class="review-grid">
          <div class="review-item">
            <span class="label">DNS Domain Name:</span>
            <span class="value">{{ config.domain_name }}</span>
          </div>
          <div class="review-item">
            <span class="label">Kerberos Realm:</span>
            <span class="value">{{ config.realm }}</span>
          </div>
          <div class="review-item">
            <span class="label">NetBIOS Domain:</span>
            <span class="value">{{ config.domain }}</span>
          </div>
          <div class="review-item">
            <span class="label">Functional Level:</span>
            <span class="value">{{ config.function_level.replace('_', ' ') }}</span>
          </div>
        </div>
      </div>

      <div class="review-section">
        <h3>🔒 Administrator Account</h3>
        <div class="review-grid">
          <div class="review-item">
            <span class="label">Username:</span>
            <span class="value">Administrator</span>
          </div>
          <div class="review-item">
            <span class="label">Password:</span>
            <span class="value">••••••••</span>
          </div>
        </div>
      </div>

      <div class="review-section">
        <h3>🌍 DNS Configuration</h3>
        <div class="review-grid">
          <div class="review-item">
            <span class="label">DNS Backend:</span>
            <span class="value">{{ config.dns_backend }}</span>
          </div>
          <div class="review-item">
            <span class="label">DNS Forwarder:</span>
            <span class="value">{{ config.dns_forwarder || 'None' }}</span>
          </div>
          <div class="review-item">
            <span class="label">Host IP:</span>
            <span class="value">{{ config.host_ip || 'Auto-detect' }}</span>
          </div>
          <div class="review-item">
            <span class="label">Server Role:</span>
            <span class="value">{{ config.server_role.toUpperCase() }}</span>
          </div>
        </div>
      </div>

      <div class="warning-box">
        <h4>⚠️ Important</h4>
        <ul>
          <li>The provisioning process will modify system configuration files</li>
          <li>This operation cannot be easily undone</li>
          <li>Make sure all settings are correct before proceeding</li>
          <li>The process may take several minutes to complete</li>
        </ul>
      </div>
    </div>

    <div class="button-group">
      <button @click="setupStore.goToStep(2)" class="btn btn-secondary">← Edit Configuration</button>
      <button @click="setupStore.nextStep()" class="btn btn-primary">
        Provision Domain →
      </button>
    </div>
  </div>
</template>

<style scoped>
.review-step {
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

.review-container {
  display: grid;
  gap: 1.5rem;
}

.review-section {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
}

.review-section h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.review-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

.review-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.label {
  font-weight: 600;
  color: #555;
}

.value {
  font-family: 'Courier New', monospace;
  color: #2c3e50;
}

.warning-box {
  background: #fff3cd;
  border-left: 4px solid #f39c12;
  padding: 1.5rem;
  border-radius: 8px;
}

.warning-box h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.warning-box ul {
  margin: 0;
  padding-left: 1.5rem;
}

.warning-box li {
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
</style>
