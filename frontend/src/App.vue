<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface HealthCheck {
  status: string
  timestamp: string
  service: string
  checks?: {
    api: string
    database: string
  }
}

const healthStatus = ref<HealthCheck | null>(null)
const detailedHealthStatus = ref<HealthCheck | null>(null)
const error = ref<string | null>(null)
const loading = ref(true)

const checkHealth = async () => {
  loading.value = true
  error.value = null

  try {
    // Basic health check
    const basicResponse = await fetch('/api/v1/health')
    if (!basicResponse.ok) throw new Error('Basic health check failed')
    healthStatus.value = await basicResponse.json()

    // Detailed health check
    const detailedResponse = await fetch('/api/v1/health/detailed')
    if (!detailedResponse.ok) throw new Error('Detailed health check failed')
    detailedHealthStatus.value = await detailedResponse.json()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unknown error occurred'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkHealth()
})
</script>

<template>
  <div class="container">
    <header>
      <h1>ADHub - Samba AD Management</h1>
      <p class="subtitle">Active Directory & Share Management Interface</p>
    </header>

    <main>
      <div class="health-card">
        <h2>System Health Status</h2>

        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>Checking system health...</p>
        </div>

        <div v-else-if="error" class="error-box">
          <h3>⚠️ Connection Error</h3>
          <p>{{ error }}</p>
          <button @click="checkHealth" class="retry-btn">Retry</button>
        </div>

        <div v-else class="health-results">
          <div class="health-section">
            <h3>Basic Health Check</h3>
            <div v-if="healthStatus" class="status-info">
              <div class="status-item">
                <span class="label">Status:</span>
                <span :class="['value', healthStatus.status]">{{ healthStatus.status }}</span>
              </div>
              <div class="status-item">
                <span class="label">Service:</span>
                <span class="value">{{ healthStatus.service }}</span>
              </div>
              <div class="status-item">
                <span class="label">Timestamp:</span>
                <span class="value">{{ new Date(healthStatus.timestamp).toLocaleString() }}</span>
              </div>
            </div>
          </div>

          <div class="health-section">
            <h3>Detailed Health Check</h3>
            <div v-if="detailedHealthStatus" class="status-info">
              <div class="status-item">
                <span class="label">Overall Status:</span>
                <span :class="['value', detailedHealthStatus.status]">{{
                  detailedHealthStatus.status
                }}</span>
              </div>
              <div v-if="detailedHealthStatus.checks" class="checks">
                <div class="check-item">
                  <span class="label">API:</span>
                  <span :class="['value', detailedHealthStatus.checks.api]">{{
                    detailedHealthStatus.checks.api
                  }}</span>
                </div>
                <div class="check-item">
                  <span class="label">Database:</span>
                  <span :class="['value', detailedHealthStatus.checks.database]">{{
                    detailedHealthStatus.checks.database
                  }}</span>
                </div>
              </div>
            </div>
          </div>

          <button @click="checkHealth" class="refresh-btn">🔄 Refresh</button>
        </div>
      </div>

      <div class="info-card">
        <h3>🎉 Stack is Working!</h3>
        <ul>
          <li>✅ Vue 3 Frontend (Vite + TypeScript)</li>
          <li>✅ FastAPI Backend (Python)</li>
          <li>✅ PostgreSQL Database</li>
          <li>✅ Docker Compose Orchestration</li>
          <li>✅ Vite Proxy Configuration</li>
          <li>✅ Health Check Endpoints</li>
        </ul>
        <p class="next-steps">
          Next: Start building your Samba AD management features! 🚀
        </p>
      </div>
    </main>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell,
    sans-serif;
}

header {
  text-align: center;
  margin-bottom: 3rem;
}

h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.1rem;
  color: #7f8c8d;
}

main {
  display: grid;
  gap: 2rem;
}

.health-card,
.info-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2,
h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.loading {
  text-align: center;
  padding: 2rem;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
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

.error-box {
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  padding: 1.5rem;
  text-align: center;
}

.error-box h3 {
  color: #c33;
  margin-bottom: 0.5rem;
}

.health-results {
  display: grid;
  gap: 1.5rem;
}

.health-section {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 1.5rem;
}

.status-info,
.checks {
  display: grid;
  gap: 0.75rem;
}

.status-item,
.check-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.label {
  font-weight: 600;
  color: #555;
}

.value {
  font-family: 'Courier New', monospace;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-weight: 500;
}

.value.healthy {
  background: #d4edda;
  color: #155724;
}

.value.degraded {
  background: #fff3cd;
  color: #856404;
}

.value.unhealthy {
  background: #f8d7da;
  color: #721c24;
}

.retry-btn,
.refresh-btn {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-btn:hover,
.refresh-btn:hover {
  background: #2980b9;
}

.refresh-btn {
  width: 100%;
}

.info-card ul {
  list-style: none;
  padding: 0;
  margin: 1rem 0;
}

.info-card li {
  padding: 0.5rem 0;
  font-size: 1.1rem;
}

.next-steps {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #e8f4f8;
  border-left: 4px solid #3498db;
  border-radius: 4px;
  font-weight: 500;
}
</style>
