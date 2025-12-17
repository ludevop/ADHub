<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { statsApi } from '@/api/stats'

const authStore = useAuthStore()

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
})

const displayName = computed(() => {
  return authStore.user?.display_name || authStore.user?.username || 'User'
})

// System stats
const stats = ref([
  { label: 'Total Users', value: '—', icon: '👥', color: '#667eea' },
  { label: 'Active Groups', value: '—', icon: '👨‍👩‍👧‍👦', color: '#764ba2' },
  { label: 'Shared Folders', value: '—', icon: '📁', color: '#3498db' },
  { label: 'DNS Records', value: '—', icon: '🌐', color: '#2ecc71' }
])

const loadingStats = ref(false)

async function fetchStats() {
  try {
    loadingStats.value = true
    const data = await statsApi.getDashboardStats()

    if (stats.value[0]) stats.value[0].value = data.total_users.toString()
    if (stats.value[1]) stats.value[1].value = data.total_groups.toString()
    if (stats.value[2]) stats.value[2].value = data.total_shares.toString()
    if (stats.value[3]) stats.value[3].value = data.total_dns_records.toString()
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  } finally {
    loadingStats.value = false
  }
}

// Quick actions
const quickActions = [
  {
    title: 'Manage Users',
    description: 'Create, edit, or remove user accounts',
    icon: '👥',
    color: '#667eea',
    disabled: true
  },
  {
    title: 'Configure Shares',
    description: 'Set up and manage file shares',
    icon: '📁',
    color: '#3498db',
    disabled: true
  },
  {
    title: 'DNS Management',
    description: 'Manage DNS records and zones',
    icon: '🌐',
    color: '#2ecc71',
    disabled: true
  },
  {
    title: 'Group Policy',
    description: 'Create and apply group policies',
    icon: '📋',
    color: '#e67e22',
    disabled: true
  }
]

// Recent activity (placeholder)
const recentActivity = ref([
  {
    action: 'System initialized',
    user: authStore.user?.username || 'Administrator',
    timestamp: new Date().toISOString(),
    icon: '✅'
  }
])

function formatTime(timestamp: string) {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`

  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`

  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
}

// Load stats on mount
onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="dashboard-home">
    <!-- Welcome section -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">{{ greeting }}, {{ displayName }}!</h1>
        <p class="welcome-subtitle">
          Welcome to ADHub - Your Samba Active Directory management dashboard
        </p>
      </div>
      <div class="welcome-decoration">
        <div class="decoration-icon">🚀</div>
      </div>
    </div>

    <!-- Stats grid -->
    <div class="stats-grid">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="stat-card"
        :style="{ '--accent-color': stat.color }"
      >
        <div class="stat-icon">{{ stat.icon }}</div>
        <div class="stat-content">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- Quick actions and recent activity -->
    <div class="content-grid">
      <!-- Quick actions -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Quick Actions</h2>
          <p class="card-subtitle">Common tasks and shortcuts</p>
        </div>
        <div class="card-body">
          <div class="actions-grid">
            <button
              v-for="action in quickActions"
              :key="action.title"
              class="action-card"
              :style="{ '--action-color': action.color }"
              :disabled="action.disabled"
            >
              <div class="action-icon">{{ action.icon }}</div>
              <div class="action-content">
                <div class="action-title">{{ action.title }}</div>
                <div class="action-description">{{ action.description }}</div>
              </div>
              <span v-if="action.disabled" class="action-badge">Coming Soon</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Recent activity -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Recent Activity</h2>
          <p class="card-subtitle">Latest changes and events</p>
        </div>
        <div class="card-body">
          <div class="activity-list">
            <div
              v-for="(activity, index) in recentActivity"
              :key="index"
              class="activity-item"
            >
              <div class="activity-icon">{{ activity.icon }}</div>
              <div class="activity-content">
                <div class="activity-action">{{ activity.action }}</div>
                <div class="activity-meta">
                  <span class="activity-user">{{ activity.user }}</span>
                  <span class="activity-separator">•</span>
                  <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- System info -->
    <div class="card system-info">
      <div class="card-header">
        <h2 class="card-title">System Information</h2>
      </div>
      <div class="card-body">
        <div class="info-grid">
          <div class="info-item">
            <div class="info-label">Domain</div>
            <div class="info-value">{{ authStore.user?.domain || '—' }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">Your Role</div>
            <div class="info-value">
              <span class="role-badge" :class="{ admin: authStore.isAdmin }">
                {{ authStore.isAdmin ? 'Administrator' : 'User' }}
              </span>
            </div>
          </div>
          <div class="info-item">
            <div class="info-label">Group Memberships</div>
            <div class="info-value">
              <div class="groups-list">
                <span
                  v-for="group in authStore.user?.groups.slice(0, 3)"
                  :key="group"
                  class="group-badge"
                >
                  {{ group }}
                </span>
                <span
                  v-if="authStore.user && authStore.user.groups.length > 3"
                  class="group-badge more"
                >
                  +{{ authStore.user.groups.length - 3 }} more
                </span>
              </div>
            </div>
          </div>
          <div class="info-item">
            <div class="info-label">Email</div>
            <div class="info-value">{{ authStore.user?.email || '—' }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-home {
  max-width: 1400px;
  margin: 0 auto;
}

/* Welcome section */
.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 2.5rem;
  color: white;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}

.welcome-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.welcome-subtitle {
  font-size: 1.125rem;
  opacity: 0.9;
  margin: 0;
}

.decoration-icon {
  font-size: 5rem;
  opacity: 0.2;
}

/* Stats grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-left: 4px solid var(--accent-color);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  font-size: 2.5rem;
  opacity: 0.8;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #7f8c8d;
  font-weight: 500;
}

/* Content grid */
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* Card */
.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.25rem 0;
}

.card-subtitle {
  font-size: 0.875rem;
  color: #7f8c8d;
  margin: 0;
}

.card-body {
  padding: 1.5rem;
}

/* Actions */
.actions-grid {
  display: grid;
  gap: 1rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border: 2px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.action-card:hover:not(:disabled) {
  border-color: var(--action-color);
  background: white;
  transform: translateX(4px);
}

.action-card:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-content {
  flex: 1;
}

.action-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.action-description {
  font-size: 0.875rem;
  color: #7f8c8d;
}

.action-badge {
  background: rgba(0, 0, 0, 0.1);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #7f8c8d;
}

/* Activity */
.activity-list {
  display: grid;
  gap: 1rem;
}

.activity-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 10px;
}

.activity-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 8px;
  flex-shrink: 0;
}

.activity-action {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.activity-meta {
  font-size: 0.875rem;
  color: #7f8c8d;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.activity-separator {
  opacity: 0.5;
}

/* System info */
.system-info {
  margin-bottom: 2rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-label {
  font-size: 0.875rem;
  color: #7f8c8d;
  font-weight: 500;
}

.info-value {
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 500;
}

.role-badge {
  display: inline-block;
  padding: 0.375rem 1rem;
  background: #e0e0e0;
  color: #2c3e50;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
}

.role-badge.admin {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.groups-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.group-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  font-size: 0.875rem;
  color: #2c3e50;
}

.group-badge.more {
  background: #e0e0e0;
  font-weight: 600;
}

/* Responsive */
@media (max-width: 768px) {
  .welcome-section {
    padding: 1.5rem;
  }

  .welcome-title {
    font-size: 1.5rem;
  }

  .decoration-icon {
    display: none;
  }

  .content-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
