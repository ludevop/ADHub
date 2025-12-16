<script setup lang="ts">
import { useSetupStore } from '@/stores/setup'

const setupStore = useSetupStore()
const emit = defineEmits(['showExistingDomainModal'])
</script>

<template>
  <div class="welcome-step">
    <h2>Welcome to ADHub Setup Wizard</h2>

    <!-- Existing domain alert -->
    <div v-if="setupStore.isProvisioned" class="existing-domain-card">
      <h3>⚠️ Existing Domain Configuration Detected</h3>
      <p>A Samba Active Directory domain is already configured on this system.</p>
      <div class="action-buttons">
        <button @click="setupStore.skipToVerification()" class="btn btn-success">
          ✓ Skip to Verification Tests
        </button>
        <button @click="emit('showExistingDomainModal')" class="btn btn-warning">
          🔧 View All Options
        </button>
      </div>
    </div>

    <div class="info-card">
      <h3>📋 What This Wizard Will Do</h3>
      <ul>
        <li>Check system prerequisites</li>
        <li>Configure Samba Active Directory domain</li>
        <li>Set up DNS services</li>
        <li>Provision the domain controller</li>
        <li>Verify installation with comprehensive tests</li>
      </ul>
    </div>

    <div class="warning-card">
      <h3>⚠️  Before You Begin</h3>
      <ul>
        <li>This wizard will configure Samba as an Active Directory Domain Controller</li>
        <li>You should have a clean system with Samba installed</li>
        <li>This process will modify system configuration files</li>
        <li>Make sure you have a backup of important data</li>
        <li>You will need root/administrator privileges</li>
      </ul>
    </div>

    <div class="requirements-card">
      <h3>✅ System Requirements</h3>
      <ul>
        <li>Samba 4.x installed</li>
        <li>At least 1GB free disk space</li>
        <li>Network connectivity</li>
        <li>Static IP address (recommended)</li>
        <li>Valid DNS forwarder</li>
      </ul>
    </div>

    <div class="button-group">
      <button @click="setupStore.nextStep()" class="btn btn-primary">
        Get Started →
      </button>
    </div>
  </div>
</template>

<style scoped>
.welcome-step {
  display: grid;
  gap: 2rem;
}

h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.info-card,
.warning-card,
.requirements-card,
.existing-domain-card {
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid;
}

.info-card {
  background: #e8f4f8;
  border-color: #3498db;
}

.warning-card {
  background: #fff3cd;
  border-color: #f39c12;
}

.requirements-card {
  background: #d4edda;
  border-color: #2ecc71;
}

.existing-domain-card {
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  border-color: #e67e22;
  border: 2px solid #e67e22;
}

.existing-domain-card p {
  margin: 0.5rem 0 1rem 0;
  color: #856404;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.info-card h3,
.warning-card h3,
.requirements-card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

ul {
  margin: 0;
  padding-left: 1.5rem;
}

li {
  margin: 0.5rem 0;
}

.button-group {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.btn {
  padding: 0.75rem 2rem;
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
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
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
