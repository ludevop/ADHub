<script setup lang="ts">
import { useSetupStore } from '@/stores/setup'
import { useRouter } from 'vue-router'

const setupStore = useSetupStore()
const router = useRouter()

function goToDashboard() {
  router.push('/dashboard')
}
</script>

<template>
  <div class="complete-step">
    <div class="success-animation">
      <div class="checkmark-circle">
        <div class="checkmark">✓</div>
      </div>
    </div>

    <h2>🎉 Setup Complete!</h2>
    <p class="description">
      Your Samba Active Directory Domain Controller has been successfully configured.
    </p>

    <div class="info-container">
      <div class="info-section">
        <h3>📝 Domain Information</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">Domain:</span>
            <span class="value">{{ setupStore.domainConfig.domain_name }}</span>
          </div>
          <div class="info-item">
            <span class="label">Realm:</span>
            <span class="value">{{ setupStore.domainConfig.realm }}</span>
          </div>
          <div class="info-item">
            <span class="label">NetBIOS:</span>
            <span class="value">{{ setupStore.domainConfig.domain }}</span>
          </div>
          <div class="info-item">
            <span class="label">Administrator:</span>
            <span class="value">Administrator</span>
          </div>
        </div>
      </div>

      <div class="info-section">
        <h3>🚀 Next Steps</h3>
        <ol>
          <li>Configure client machines to use this server as their DNS server</li>
          <li>Join computers to the domain</li>
          <li>Create user accounts and groups</li>
          <li>Set up file shares</li>
          <li>Configure Group Policies</li>
        </ol>
      </div>

      <div class="info-section">
        <h3>📚 Quick Tips</h3>
        <ul>
          <li>
            <strong>DNS Server:</strong> Point clients to this server's IP for DNS resolution
          </li>
          <li><strong>Time Sync:</strong> Ensure clients sync time with this server (NTP)</li>
          <li><strong>Firewall:</strong> Keep ports 53, 88, 389, 445, 636 open</li>
          <li><strong>Backups:</strong> Regularly backup /var/lib/samba and /etc/samba</li>
        </ul>
      </div>

      <div class="warning-section">
        <h3>🔒 Security Reminders</h3>
        <ul>
          <li>Store your Administrator password securely</li>
          <li>Keep your system and Samba updated</li>
          <li>Monitor logs regularly for suspicious activity</li>
          <li>Use strong passwords for all user accounts</li>
          <li>Enable SSL/TLS for LDAPS connections</li>
        </ul>
      </div>
    </div>

    <div class="button-group">
      <button @click="setupStore.resetWizard()" class="btn btn-secondary">🔄 Run Setup Again</button>
      <button @click="goToDashboard" class="btn btn-primary">Go to Dashboard →</button>
    </div>
  </div>
</template>

<style scoped>
.complete-step {
  display: grid;
  gap: 2rem;
  text-align: center;
}

.success-animation {
  display: flex;
  justify-content: center;
  margin: 1rem 0;
}

.checkmark-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: scaleIn 0.5s ease-out;
  box-shadow: 0 4px 20px rgba(46, 204, 113, 0.4);
}

.checkmark {
  font-size: 3rem;
  color: white;
  animation: checkmark 0.5s ease-in 0.3s both;
}

@keyframes scaleIn {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes checkmark {
  0% {
    opacity: 0;
    transform: scale(0);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

h2 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.description {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.info-container {
  display: grid;
  gap: 1.5rem;
  text-align: left;
}

.info-section,
.warning-section {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
}

.warning-section {
  background: #fff3cd;
  border-left: 4px solid #f39c12;
}

.info-section h3,
.warning-section h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.info-grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.info-item {
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

ol,
ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

li {
  margin: 0.5rem 0;
  line-height: 1.6;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 1rem;
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

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}
</style>
