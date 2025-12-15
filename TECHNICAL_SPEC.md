# ADHub - Detailed Technical Specification

## Table of Contents
1. [Technology Stack - Complete Library List](#technology-stack)
2. [Feature Specifications](#feature-specifications)
3. [Component Architecture](#component-architecture)
4. [Data Flow Diagrams](#data-flow)
5. [Implementation Details](#implementation-details)

---

## Technology Stack - Complete Library List

### Backend (Python/FastAPI)

#### Core Framework
```python
# requirements.txt
fastapi==0.109.0              # Web framework
uvicorn[standard]==0.27.0     # ASGI server with performance extras
pydantic==2.5.0              # Data validation
pydantic-settings==2.1.0     # Settings management
```

#### Samba Integration
```python
# Samba libraries (system packages)
# Install via: apt-get install python3-samba samba-dev
python-samba                  # Official Samba Python bindings
ldap3==2.9.1                 # LDAP client for authentication
```

#### Database & ORM
```python
sqlalchemy==2.0.25           # SQL toolkit and ORM
alembic==1.13.1              # Database migrations
asyncpg==0.29.0              # Async PostgreSQL driver
psycopg2-binary==2.9.9       # Sync PostgreSQL driver (for Alembic)
```

#### Authentication & Security
```python
python-jose[cryptography]==3.3.0  # JWT token handling
passlib[bcrypt]==1.7.4            # Password hashing (for service accounts)
python-multipart==0.0.6           # Form data parsing
cryptography==41.0.7              # Encryption utilities
```

#### Caching & Sessions
```python
redis==5.0.1                 # Redis client
aioredis==2.0.1             # Async Redis client
hiredis==2.3.2              # High-performance Redis parser
```

#### API Features
```python
slowapi==0.1.9              # Rate limiting
python-dotenv==1.0.0        # Environment variable management
```

#### Monitoring & Logging
```python
prometheus-client==0.19.0    # Prometheus metrics
python-json-logger==2.0.7   # Structured JSON logging
```

#### Background Tasks
```python
celery==5.3.4               # Distributed task queue
celery[redis]==5.3.4        # Redis backend for Celery
flower==2.0.1               # Celery monitoring
```

#### Utilities
```python
python-dateutil==2.8.2      # Date/time utilities
pytz==2023.3                # Timezone support
tenacity==8.2.3             # Retry logic with backoff
httpx==0.26.0               # HTTP client (for health checks)
```

#### Testing
```python
pytest==7.4.3               # Testing framework
pytest-asyncio==0.21.1      # Async test support
pytest-cov==4.1.0           # Coverage reporting
pytest-mock==3.12.0         # Mocking utilities
httpx==0.26.0               # Test client
faker==22.0.0               # Test data generation
```

---

### Frontend (Vue 3 + TypeScript)

#### Core Framework
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "typescript": "^5.3.3"
  }
}
```

#### UI Framework: **PrimeVue** (Complete Ecosystem)
```json
{
  "dependencies": {
    "primevue": "^3.48.0",          // Core component library
    "primeicons": "^6.0.1",         // Icon library
    "primeflex": "^3.3.1",          // Flexbox utility library

    // Chart library for dashboards
    "chart.js": "^4.4.1",
    "primevue/chart": "^3.48.0",    // PrimeVue chart components

    // Additional PrimeVue modules
    "@primevue/themes": "^3.48.0"   // Theme engine
  }
}
```

**Why PrimeVue?**
- ✅ 90+ components out of the box
- ✅ Excellent data table (DataTable) with filtering, sorting, pagination
- ✅ Built-in form validation
- ✅ Tree components (perfect for OU/AD structure)
- ✅ Toast/message system for notifications
- ✅ Themes (customizable for dark/light mode)
- ✅ Active development and good documentation
- ✅ TypeScript support
- ✅ No jQuery dependencies (modern, lightweight)

#### HTTP Client
```json
{
  "dependencies": {
    "axios": "^1.6.5",              // HTTP client
    "axios-auth-refresh": "^3.3.6"  // Auto token refresh
  }
}
```

#### State Management & Utilities
```json
{
  "dependencies": {
    "pinia": "^2.1.7",              // State management
    "pinia-plugin-persistedstate": "^3.2.1",  // Persist state
    "@vueuse/core": "^10.7.0",      // Composition utilities
    "@vueuse/integrations": "^10.7.0"
  }
}
```

#### Form Validation
```json
{
  "dependencies": {
    "vee-validate": "^4.12.4",      // Form validation
    "yup": "^1.3.3",                // Schema validation
    "zod": "^3.22.4"                // Alternative schema validation (TS-first)
  }
}
```

#### Real-time Communication
```json
{
  "dependencies": {
    "eventsource": "^2.0.2",        // Server-Sent Events polyfill
    "reconnecting-eventsource": "^1.6.2"  // SSE with reconnection
  }
}
```

#### Date/Time Handling
```json
{
  "dependencies": {
    "date-fns": "^3.0.6",           // Date utilities (modern, tree-shakeable)
    "date-fns-tz": "^2.0.0"         // Timezone support
  }
}
```

#### Utilities
```json
{
  "dependencies": {
    "lodash-es": "^4.17.21",        // Utility functions (ES modules)
    "uuid": "^9.0.1",               // UUID generation
    "file-saver": "^2.0.5",         // File downloads
    "papaparse": "^5.4.1"           // CSV parsing/generation
  }
}
```

#### Code Quality
```json
{
  "devDependencies": {
    "eslint": "^8.56.0",
    "eslint-plugin-vue": "^9.19.2",
    "@typescript-eslint/eslint-plugin": "^6.18.1",
    "@typescript-eslint/parser": "^6.18.1",
    "prettier": "^3.1.1",
    "prettier-plugin-organize-imports": "^3.2.4"
  }
}
```

#### Testing
```json
{
  "devDependencies": {
    "vitest": "^1.1.3",             // Test framework (Vite-native)
    "@vue/test-utils": "^2.4.3",    // Vue testing utilities
    "happy-dom": "^12.10.3",        // DOM implementation for tests
    "playwright": "^1.40.1",        // E2E testing
    "@playwright/test": "^1.40.1"
  }
}
```

#### Build Tools
```json
{
  "devDependencies": {
    "vite": "^5.0.11",
    "@vitejs/plugin-vue": "^5.0.2",
    "vite-plugin-pwa": "^0.17.4",   // Progressive Web App
    "rollup-plugin-visualizer": "^5.12.0"  // Bundle analysis
  }
}
```

---

## Feature Specifications

### 1. Authentication & User Management

#### 1.1 Login System

**Components:**
- `LoginView.vue` - Main login page
- `LoginForm.vue` - Login form component

**PrimeVue Components Used:**
- `InputText` - Username/password fields
- `Password` - Password field with toggle visibility
- `Button` - Login button with loading state
- `Message` - Error messages
- `Card` - Login card container

**Features:**
```
Login System
├── Authentication
│   ├── Username/password input
│   ├── "Remember me" checkbox (store username only)
│   ├── Password visibility toggle
│   ├── Enter key submit
│   └── Loading state during auth
├── Validation
│   ├── Required field validation
│   ├── Real-time error display
│   └── LDAP error translation
├── Security
│   ├── Rate limiting display (attempts remaining)
│   ├── Account lockout notice
│   └── HTTPS-only warning
└── UX Features
    ├── Auto-focus username field
    ├── Tab navigation
    ├── Responsive design (mobile-friendly)
    └── Dark/light theme support
```

**Implementation:**
```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'
import type { LoginCredentials, User, AuthTokens } from '@/types/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    accessToken: null as string | null,
    refreshToken: null as string | null,
    isAuthenticated: false,
    loading: false,
    error: null as string | null
  }),

  getters: {
    userRoles: (state) => state.user?.roles || [],
    hasRole: (state) => (role: string) =>
      state.user?.roles.includes(role) || false,
    isSuperAdmin: (state) =>
      state.user?.roles.includes('super_admin') || false
  },

  actions: {
    async login(credentials: LoginCredentials) {
      this.loading = true
      this.error = null

      try {
        const response = await authApi.login(credentials)

        this.accessToken = response.access_token
        this.refreshToken = response.refresh_token
        this.user = response.user
        this.isAuthenticated = true

        // Store tokens
        localStorage.setItem('refreshToken', response.refresh_token)

        return response.user
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Login failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        await authApi.logout()
      } finally {
        this.user = null
        this.accessToken = null
        this.refreshToken = null
        this.isAuthenticated = false
        localStorage.removeItem('refreshToken')
      }
    },

    async refreshAccessToken() {
      const refreshToken = this.refreshToken || localStorage.getItem('refreshToken')

      if (!refreshToken) {
        this.logout()
        return false
      }

      try {
        const response = await authApi.refresh(refreshToken)
        this.accessToken = response.access_token
        return true
      } catch (error) {
        this.logout()
        return false
      }
    }
  },

  persist: {
    paths: ['user'] // Only persist user info, not tokens
  }
})
```

```vue
<!-- views/LoginView.vue -->
<template>
  <div class="login-container">
    <Card class="login-card">
      <template #header>
        <div class="logo-container">
          <img src="@/assets/logo.svg" alt="ADHub" />
          <h1>ADHub</h1>
          <p>Samba Active Directory Management</p>
        </div>
      </template>

      <template #content>
        <form @submit.prevent="handleLogin">
          <div class="field">
            <label for="username">Username</label>
            <InputText
              id="username"
              v-model="credentials.username"
              :class="{ 'p-invalid': errors.username }"
              placeholder="Enter your username"
              autocomplete="username"
              autofocus
            />
            <small class="p-error" v-if="errors.username">
              {{ errors.username }}
            </small>
          </div>

          <div class="field">
            <label for="password">Password</label>
            <Password
              id="password"
              v-model="credentials.password"
              :class="{ 'p-invalid': errors.password }"
              placeholder="Enter your password"
              :feedback="false"
              toggle-mask
              autocomplete="current-password"
            />
            <small class="p-error" v-if="errors.password">
              {{ errors.password }}
            </small>
          </div>

          <div class="field-checkbox">
            <Checkbox
              id="remember"
              v-model="rememberMe"
              :binary="true"
            />
            <label for="remember">Remember username</label>
          </div>

          <Message v-if="authStore.error" severity="error" :closable="false">
            {{ authStore.error }}
          </Message>

          <Button
            type="submit"
            label="Sign In"
            :loading="authStore.loading"
            icon="pi pi-sign-in"
            class="w-full"
          />
        </form>
      </template>

      <template #footer>
        <div class="footer-info">
          <i class="pi pi-info-circle"></i>
          <span>Use your Active Directory credentials</span>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import Message from 'primevue/message'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const credentials = reactive({
  username: localStorage.getItem('rememberedUsername') || '',
  password: ''
})

const rememberMe = ref(!!localStorage.getItem('rememberedUsername'))
const errors = reactive({
  username: '',
  password: ''
})

const validateForm = () => {
  errors.username = credentials.username ? '' : 'Username is required'
  errors.password = credentials.password ? '' : 'Password is required'

  return !errors.username && !errors.password
}

const handleLogin = async () => {
  if (!validateForm()) return

  try {
    await authStore.login(credentials)

    // Remember username if checked
    if (rememberMe.value) {
      localStorage.setItem('rememberedUsername', credentials.username)
    } else {
      localStorage.removeItem('rememberedUsername')
    }

    toast.add({
      severity: 'success',
      summary: 'Welcome back!',
      detail: `Logged in as ${credentials.username}`,
      life: 3000
    })

    router.push('/dashboard')
  } catch (error) {
    // Error is handled in store and displayed in Message component
  }
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.login-card {
  width: 100%;
  max-width: 450px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.logo-container {
  text-align: center;
  padding: 2rem 0 1rem;

  img {
    height: 60px;
    margin-bottom: 1rem;
  }

  h1 {
    margin: 0;
    font-size: 2rem;
    color: var(--primary-color);
  }

  p {
    margin: 0.5rem 0 0;
    color: var(--text-color-secondary);
  }
}

.field {
  margin-bottom: 1.5rem;

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
  }
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.footer-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}
</style>
```

#### 1.2 User Profile & Preferences

**Components:**
- `UserProfile.vue` - User profile page
- `UserPreferences.vue` - Preferences dialog
- `PasswordChange.vue` - Change password (AD password)

**Features:**
```
User Profile
├── Display Information
│   ├── Username (sAMAccountName)
│   ├── Display name
│   ├── Email address
│   ├── AD groups (with badges)
│   ├── Application roles (with badges)
│   ├── Last login timestamp
│   └── Account status
├── Preferences
│   ├── Theme selection (light/dark/system)
│   ├── Language preference
│   ├── Date/time format
│   ├── Default page size (tables)
│   ├── Dashboard layout
│   └── Notification preferences
└── Actions
    ├── Change AD password (redirects to password policy info)
    ├── View audit logs (own actions)
    └── Export preferences
```

**PrimeVue Components:**
- `Card` - Profile container
- `Avatar` - User avatar (initials)
- `Chip` - Role/group badges
- `Divider` - Section separators
- `TabView` - Tabs for Info/Preferences/Audit
- `Dropdown` - Theme/language selection
- `Slider` - Page size selection

---

### 2. Dashboard

#### 2.1 Overview Dashboard

**Components:**
- `DashboardView.vue` - Main dashboard
- `StatCard.vue` - Statistic cards
- `RecentActivityTable.vue` - Recent actions
- `SystemHealth.vue` - Health indicators
- `QuickActions.vue` - Quick action buttons

**Features:**
```
Dashboard
├── Statistics Overview
│   ├── Total Users (with trend)
│   ├── Total Groups
│   ├── Total Shares
│   ├── Active Connections (real-time)
│   ├── Failed Login Attempts (last 24h)
│   └── Disk Usage
├── Charts
│   ├── Connection History (line chart - last 7 days)
│   ├── User Activity (bar chart - top 10 users)
│   ├── Share Usage (pie chart)
│   └── Login Activity (area chart - last 30 days)
├── System Health
│   ├── Samba Services Status
│   │   ├── smbd (green/yellow/red indicator)
│   │   ├── nmbd
│   │   ├── winbindd
│   │   └── samba-dcerpcd
│   ├── LDAP Connectivity
│   ├── Database Status
│   ├── Redis Status
│   └── Disk Space Warning
├── Recent Activity Feed
│   ├── Last 10 administrative actions
│   ├── User who performed action
│   ├── Timestamp (relative, e.g., "5 minutes ago")
│   ├── Action type with icon
│   └── Click to view details
└── Quick Actions
    ├── Create User (button)
    ├── Create Group (button)
    ├── Create Share (button)
    ├── View All Connections (button)
    └── Run Health Check (button)
```

**PrimeVue Components:**
- `Card` - Stat cards, sections
- `Chart` - All charts (Line, Bar, Pie, Doughnut)
- `Timeline` - Recent activity
- `Tag` - Status indicators
- `ProgressBar` - Disk usage
- `Button` - Quick actions
- `Badge` - Notification counts

**Implementation:**
```vue
<!-- views/DashboardView.vue -->
<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Dashboard</h1>
      <Button
        icon="pi pi-refresh"
        label="Refresh"
        @click="refreshData"
        :loading="loading"
        text
      />
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-icon users">
              <i class="pi pi-users"></i>
            </div>
            <div class="stat-details">
              <div class="stat-label">Total Users</div>
              <div class="stat-value">{{ stats.totalUsers }}</div>
              <div class="stat-change positive">
                <i class="pi pi-arrow-up"></i>
                <span>+12 this week</span>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-icon groups">
              <i class="pi pi-sitemap"></i>
            </div>
            <div class="stat-details">
              <div class="stat-label">Groups</div>
              <div class="stat-value">{{ stats.totalGroups }}</div>
            </div>
          </div>
        </template>
      </Card>

      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-icon shares">
              <i class="pi pi-folder"></i>
            </div>
            <div class="stat-details">
              <div class="stat-label">Shares</div>
              <div class="stat-value">{{ stats.totalShares }}</div>
            </div>
          </div>
        </template>
      </Card>

      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-icon connections">
              <i class="pi pi-link"></i>
            </div>
            <div class="stat-details">
              <div class="stat-label">Active Connections</div>
              <div class="stat-value">{{ stats.activeConnections }}</div>
              <div class="stat-badge">
                <Badge :value="stats.activeConnections" severity="success" />
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <div class="dashboard-grid">
      <!-- Charts Section -->
      <div class="charts-section">
        <Card>
          <template #title>Connection Activity</template>
          <template #content>
            <Chart type="line" :data="connectionChartData" :options="chartOptions" />
          </template>
        </Card>

        <Card>
          <template #title>Top Active Users</template>
          <template #content>
            <Chart type="bar" :data="userActivityData" :options="barChartOptions" />
          </template>
        </Card>
      </div>

      <!-- Sidebar Section -->
      <div class="sidebar-section">
        <!-- System Health -->
        <Card>
          <template #title>System Health</template>
          <template #content>
            <div class="health-items">
              <div class="health-item">
                <span class="health-label">smbd</span>
                <Tag :value="serviceStatus.smbd.status" :severity="getStatusSeverity(serviceStatus.smbd.status)" />
              </div>
              <div class="health-item">
                <span class="health-label">nmbd</span>
                <Tag :value="serviceStatus.nmbd.status" :severity="getStatusSeverity(serviceStatus.nmbd.status)" />
              </div>
              <div class="health-item">
                <span class="health-label">winbindd</span>
                <Tag :value="serviceStatus.winbindd.status" :severity="getStatusSeverity(serviceStatus.winbindd.status)" />
              </div>
              <div class="health-item">
                <span class="health-label">LDAP</span>
                <Tag :value="serviceStatus.ldap.status" :severity="getStatusSeverity(serviceStatus.ldap.status)" />
              </div>
            </div>
          </template>
        </Card>

        <!-- Recent Activity -->
        <Card>
          <template #title>Recent Activity</template>
          <template #content>
            <Timeline :value="recentActivities" class="activity-timeline">
              <template #content="{ item }">
                <div class="activity-item">
                  <div class="activity-header">
                    <span class="activity-user">{{ item.username }}</span>
                    <span class="activity-time">{{ formatTime(item.timestamp) }}</span>
                  </div>
                  <div class="activity-action">
                    <i :class="getActionIcon(item.action)"></i>
                    {{ item.action }}
                  </div>
                  <div class="activity-target">{{ item.target }}</div>
                </div>
              </template>
            </Timeline>
          </template>
        </Card>

        <!-- Quick Actions -->
        <Card>
          <template #title>Quick Actions</template>
          <template #content>
            <div class="quick-actions">
              <Button
                label="Create User"
                icon="pi pi-user-plus"
                @click="router.push('/users/create')"
                class="p-button-outlined w-full"
              />
              <Button
                label="Create Group"
                icon="pi pi-sitemap"
                @click="router.push('/groups/create')"
                class="p-button-outlined w-full"
              />
              <Button
                label="Create Share"
                icon="pi pi-folder-open"
                @click="router.push('/shares/create')"
                class="p-button-outlined w-full"
              />
              <Button
                label="View Connections"
                icon="pi pi-chart-line"
                @click="router.push('/monitoring/connections')"
                class="p-button-outlined w-full"
              />
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'
import { formatDistanceToNow } from 'date-fns'
import Card from 'primevue/card'
import Chart from 'primevue/chart'
import Timeline from 'primevue/timeline'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Badge from 'primevue/badge'

const router = useRouter()
const dashboardStore = useDashboardStore()

const loading = ref(false)

const stats = computed(() => dashboardStore.statistics)
const serviceStatus = computed(() => dashboardStore.serviceStatus)
const recentActivities = computed(() => dashboardStore.recentActivities)

const connectionChartData = computed(() => ({
  labels: dashboardStore.connectionHistory.labels,
  datasets: [
    {
      label: 'Active Connections',
      data: dashboardStore.connectionHistory.data,
      fill: true,
      borderColor: '#42A5F5',
      backgroundColor: 'rgba(66, 165, 245, 0.2)',
      tension: 0.4
    }
  ]
}))

const userActivityData = computed(() => ({
  labels: dashboardStore.topUsers.map(u => u.username),
  datasets: [
    {
      label: 'Activity Count',
      data: dashboardStore.topUsers.map(u => u.count),
      backgroundColor: '#66BB6A'
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  }
}

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  plugins: {
    legend: {
      display: false
    }
  }
}

const getStatusSeverity = (status: string) => {
  const severityMap: Record<string, 'success' | 'warning' | 'danger'> = {
    'running': 'success',
    'degraded': 'warning',
    'stopped': 'danger'
  }
  return severityMap[status.toLowerCase()] || 'warning'
}

const formatTime = (timestamp: string) => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

const getActionIcon = (action: string) => {
  const iconMap: Record<string, string> = {
    'create_user': 'pi pi-user-plus',
    'delete_user': 'pi pi-user-minus',
    'create_share': 'pi pi-folder-plus',
    'delete_share': 'pi pi-folder-minus',
    'modify_group': 'pi pi-sitemap'
  }
  return iconMap[action] || 'pi pi-circle-fill'
}

const refreshData = async () => {
  loading.value = true
  try {
    await dashboardStore.fetchAll()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  dashboardStore.fetchAll()

  // Auto-refresh every 30 seconds
  const interval = setInterval(() => {
    dashboardStore.fetchStatistics()
    dashboardStore.fetchServiceStatus()
  }, 30000)

  // Cleanup on unmount
  onUnmounted(() => clearInterval(interval))
})
</script>

<style scoped lang="scss">
.dashboard {
  padding: 2rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;

  h1 {
    margin: 0;
    font-size: 2rem;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  .stat-content {
    display: flex;
    gap: 1rem;
  }

  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    color: white;

    &.users { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    &.groups { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    &.shares { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    &.connections { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
  }

  .stat-details {
    flex: 1;
  }

  .stat-label {
    font-size: 0.875rem;
    color: var(--text-color-secondary);
    margin-bottom: 0.25rem;
  }

  .stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-color);
  }

  .stat-change {
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.25rem;

    &.positive {
      color: #22c55e;
    }
  }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 1.5rem;

  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}

.charts-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  .p-card {
    height: 350px;
  }
}

.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.health-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.health-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--surface-border);

  &:last-child {
    border-bottom: none;
  }
}

.activity-timeline {
  .activity-item {
    padding: 0.5rem 0;
  }

  .activity-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.25rem;
  }

  .activity-user {
    font-weight: 600;
  }

  .activity-time {
    font-size: 0.75rem;
    color: var(--text-color-secondary);
  }

  .activity-action {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
  }

  .activity-target {
    font-size: 0.875rem;
    color: var(--text-color-secondary);
  }
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
</style>
```

---

### 3. SMB Share Management

#### 3.1 Share List View

**Components:**
- `ShareListView.vue` - Main list with DataTable
- `ShareQuickActions.vue` - Bulk operations toolbar
- `ShareDeleteDialog.vue` - Confirmation dialog
- `ShareExportDialog.vue` - Export configuration

**Features:**
```
Share List
├── Data Display
│   ├── DataTable with virtual scrolling (large datasets)
│   ├── Columns: Name, Path, Status, Permissions, Connections, Actions
│   ├── Column sorting (multi-column)
│   ├── Column reordering (drag-drop)
│   ├── Column visibility toggle
│   └── Responsive (stacked on mobile)
├── Filtering
│   ├── Global search (name, path, comment)
│   ├── Column filters (dropdowns)
│   ├── Status filter (Active/Inactive/Error)
│   ├── Permission filter (Read-only/Read-Write/Custom)
│   └── Filter presets (Recently created, Most active, etc.)
├── Selection & Bulk Operations
│   ├── Row selection (checkbox)
│   ├── Select all/none
│   ├── Bulk activate/deactivate
│   ├── Bulk delete (with confirmation)
│   └── Bulk export configuration
├── Export Options
│   ├── Export to CSV
│   ├── Export to Excel
│   ├── Export to JSON
│   └── Export smb.conf snippet
├── Row Actions
│   ├── Edit share
│   ├── Manage permissions (ACL editor)
│   ├── View active connections
│   ├── Copy UNC path (\\server\share)
│   ├── Delete share
│   └── Duplicate share
└── Pagination & Performance
    ├── Server-side pagination
    ├── Configurable page size (10/25/50/100)
    ├── Lazy loading for large datasets
    └── Real-time connection count updates (SSE)
```

**PrimeVue Components:**
- `DataTable` with `Column` - Main table
- `InputText` - Global filter
- `MultiSelect` - Column visibility
- `Dropdown` - Status/permission filters
- `Button`, `SplitButton` - Actions
- `ConfirmDialog` - Delete confirmation
- `Menu` - Row action menu
- `Tag` - Status badges
- `Badge` - Connection count
- `ProgressBar` - Disk usage
- `Skeleton` - Loading states

**Implementation:**
```vue
<!-- views/shares/ShareListView.vue -->
<template>
  <div class="share-list">
    <div class="list-header">
      <h1>SMB Shares</h1>
      <div class="header-actions">
        <Button
          icon="pi pi-refresh"
          label="Refresh"
          @click="loadShares"
          :loading="loading"
          text
        />
        <Button
          icon="pi pi-plus"
          label="Create Share"
          @click="router.push('/shares/create')"
          severity="success"
        />
      </div>
    </div>

    <!-- Toolbar with bulk actions -->
    <div class="toolbar" v-if="selectedShares.length > 0">
      <div class="selected-info">
        <span>{{ selectedShares.length }} share(s) selected</span>
      </div>
      <div class="bulk-actions">
        <Button
          icon="pi pi-check"
          label="Activate"
          @click="bulkActivate"
          outlined
        />
        <Button
          icon="pi pi-times"
          label="Deactivate"
          @click="bulkDeactivate"
          outlined
        />
        <Button
          icon="pi pi-download"
          label="Export"
          @click="showExportDialog = true"
          outlined
        />
        <Button
          icon="pi pi-trash"
          label="Delete"
          @click="confirmBulkDelete"
          severity="danger"
          outlined
        />
      </div>
    </div>

    <!-- DataTable -->
    <Card>
      <template #content>
        <DataTable
          v-model:selection="selectedShares"
          v-model:filters="filters"
          :value="shares"
          :loading="loading"
          :rows="pageSize"
          :totalRecords="totalRecords"
          :lazy="true"
          :paginator="true"
          :rowsPerPageOptions="[10, 25, 50, 100]"
          :globalFilterFields="['name', 'path', 'comment']"
          filterDisplay="row"
          dataKey="id"
          @page="onPage"
          @sort="onSort"
          @filter="onFilter"
          removableSort
          sortMode="multiple"
          responsiveLayout="scroll"
          showGridlines
          stripedRows
        >
          <template #header>
            <div class="table-header">
              <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText
                  v-model="filters['global'].value"
                  placeholder="Search shares..."
                />
              </span>
              <MultiSelect
                v-model="visibleColumns"
                :options="columns"
                optionLabel="header"
                placeholder="Columns"
                display="chip"
              />
            </div>
          </template>

          <template #empty>
            <div class="empty-state">
              <i class="pi pi-folder" style="font-size: 3rem"></i>
              <h3>No shares found</h3>
              <p>Create your first SMB share to get started</p>
              <Button
                icon="pi pi-plus"
                label="Create Share"
                @click="router.push('/shares/create')"
              />
            </div>
          </template>

          <Column selectionMode="multiple" headerStyle="width: 3rem" />

          <Column
            field="name"
            header="Share Name"
            :sortable="true"
            :showFilterMenu="false"
          >
            <template #body="{ data }">
              <div class="share-name">
                <i class="pi pi-folder" style="margin-right: 0.5rem"></i>
                <router-link :to="`/shares/${data.id}`">
                  {{ data.name }}
                </router-link>
              </div>
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <InputText
                v-model="filterModel.value"
                @input="filterCallback()"
                placeholder="Search by name"
              />
            </template>
          </Column>

          <Column field="path" header="Path" :sortable="true">
            <template #body="{ data }">
              <code class="path-code">{{ data.path }}</code>
            </template>
          </Column>

          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag
                :value="data.status"
                :severity="getStatusSeverity(data.status)"
              />
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <Dropdown
                v-model="filterModel.value"
                :options="statusOptions"
                @change="filterCallback()"
                placeholder="All"
                showClear
              />
            </template>
          </Column>

          <Column field="permissions" header="Permissions" :sortable="true">
            <template #body="{ data }">
              <Tag
                :value="getPermissionLabel(data.read_only)"
                :severity="data.read_only ? 'info' : 'warning'"
              />
            </template>
          </Column>

          <Column field="active_connections" header="Connections">
            <template #body="{ data }">
              <Badge :value="data.active_connections" severity="success" />
            </template>
          </Column>

          <Column field="comment" header="Description">
            <template #body="{ data }">
              <span class="text-secondary">{{ data.comment || '—' }}</span>
            </template>
          </Column>

          <Column header="Actions" :exportable="false" frozen alignFrozen="right">
            <template #body="{ data }">
              <SplitButton
                icon="pi pi-pencil"
                label="Edit"
                @click="editShare(data)"
                :model="getRowActions(data)"
                size="small"
                outlined
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Export Dialog -->
    <Dialog
      v-model:visible="showExportDialog"
      header="Export Shares"
      :modal="true"
      :style="{ width: '450px' }"
    >
      <div class="export-options">
        <div class="field">
          <label>Export Format</label>
          <div class="flex flex-column gap-2">
            <div class="flex align-items-center">
              <RadioButton
                v-model="exportFormat"
                inputId="csv"
                value="csv"
              />
              <label for="csv" class="ml-2">CSV</label>
            </div>
            <div class="flex align-items-center">
              <RadioButton
                v-model="exportFormat"
                inputId="excel"
                value="excel"
              />
              <label for="excel" class="ml-2">Excel (XLSX)</label>
            </div>
            <div class="flex align-items-center">
              <RadioButton
                v-model="exportFormat"
                inputId="json"
                value="json"
              />
              <label for="json" class="ml-2">JSON</label>
            </div>
            <div class="flex align-items-center">
              <RadioButton
                v-model="exportFormat"
                inputId="smbconf"
                value="smbconf"
              />
              <label for="smbconf" class="ml-2">smb.conf snippet</label>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Cancel" @click="showExportDialog = false" text />
        <Button
          label="Export"
          icon="pi pi-download"
          @click="exportShares"
          autofocus
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation -->
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useShareStore } from '@/stores/share'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { FilterMatchMode } from 'primevue/api'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Card from 'primevue/card'
import Button from 'primevue/button'
import SplitButton from 'primevue/splitbutton'
import InputText from 'primevue/inputtext'
import MultiSelect from 'primevue/multiselect'
import Dropdown from 'primevue/dropdown'
import Tag from 'primevue/tag'
import Badge from 'primevue/badge'
import Dialog from 'primevue/dialog'
import RadioButton from 'primevue/radiobutton'
import ConfirmDialog from 'primevue/confirmdialog'

const router = useRouter()
const shareStore = useShareStore()
const confirm = useConfirm()
const toast = useToast()

const loading = ref(false)
const selectedShares = ref([])
const showExportDialog = ref(false)
const exportFormat = ref('csv')
const pageSize = ref(25)
const totalRecords = ref(0)

const shares = computed(() => shareStore.shares)

const columns = ref([
  { field: 'name', header: 'Share Name' },
  { field: 'path', header: 'Path' },
  { field: 'status', header: 'Status' },
  { field: 'permissions', header: 'Permissions' },
  { field: 'active_connections', header: 'Connections' },
  { field: 'comment', header: 'Description' }
])

const visibleColumns = ref(columns.value)

const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
  name: { value: null, matchMode: FilterMatchMode.CONTAINS },
  status: { value: null, matchMode: FilterMatchMode.EQUALS }
})

const statusOptions = ref(['Active', 'Inactive', 'Error'])

const getStatusSeverity = (status: string) => {
  const map: Record<string, any> = {
    'Active': 'success',
    'Inactive': 'warning',
    'Error': 'danger'
  }
  return map[status] || 'info'
}

const getPermissionLabel = (readOnly: boolean) => {
  return readOnly ? 'Read-Only' : 'Read-Write'
}

const getRowActions = (share: any) => [
  {
    label: 'Manage Permissions',
    icon: 'pi pi-lock',
    command: () => router.push(`/shares/${share.id}/permissions`)
  },
  {
    label: 'View Connections',
    icon: 'pi pi-users',
    command: () => router.push(`/shares/${share.id}/connections`)
  },
  {
    separator: true
  },
  {
    label: 'Copy UNC Path',
    icon: 'pi pi-copy',
    command: () => copyUNCPath(share)
  },
  {
    label: 'Duplicate',
    icon: 'pi pi-clone',
    command: () => duplicateShare(share)
  },
  {
    separator: true
  },
  {
    label: 'Delete',
    icon: 'pi pi-trash',
    command: () => confirmDelete(share),
    class: 'text-red-500'
  }
]

const loadShares = async (params = {}) => {
  loading.value = true
  try {
    await shareStore.fetchShares(params)
    totalRecords.value = shareStore.totalCount
  } finally {
    loading.value = false
  }
}

const onPage = (event: any) => {
  loadShares({
    offset: event.first,
    limit: event.rows
  })
}

const onSort = (event: any) => {
  loadShares({
    sortField: event.sortField,
    sortOrder: event.sortOrder
  })
}

const onFilter = (event: any) => {
  loadShares({
    filters: event.filters
  })
}

const editShare = (share: any) => {
  router.push(`/shares/${share.id}/edit`)
}

const copyUNCPath = (share: any) => {
  const uncPath = `\\\\${window.location.hostname}\\${share.name}`
  navigator.clipboard.writeText(uncPath)
  toast.add({
    severity: 'success',
    summary: 'Copied',
    detail: `UNC path copied to clipboard`,
    life: 3000
  })
}

const duplicateShare = async (share: any) => {
  try {
    await shareStore.duplicateShare(share.id)
    toast.add({
      severity: 'success',
      summary: 'Share Duplicated',
      detail: `Created copy of ${share.name}`,
      life: 3000
    })
    loadShares()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to duplicate share',
      life: 5000
    })
  }
}

const confirmDelete = (share: any) => {
  confirm.require({
    message: `Are you sure you want to delete share "${share.name}"?`,
    header: 'Confirm Deletion',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await shareStore.deleteShare(share.id)
        toast.add({
          severity: 'success',
          summary: 'Deleted',
          detail: `Share "${share.name}" deleted`,
          life: 3000
        })
        loadShares()
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete share',
          life: 5000
        })
      }
    }
  })
}

const bulkActivate = async () => {
  // Implementation
}

const bulkDeactivate = async () => {
  // Implementation
}

const confirmBulkDelete = () => {
  confirm.require({
    message: `Delete ${selectedShares.value.length} selected share(s)?`,
    header: 'Confirm Bulk Deletion',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      // Implementation
    }
  })
}

const exportShares = async () => {
  // Implementation based on exportFormat.value
  showExportDialog.value = false
}

onMounted(() => {
  loadShares()
})
</script>

<style scoped lang="scss">
.share-list {
  padding: 2rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;

  h1 {
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
  }
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--primary-50);
  border-radius: 6px;
  margin-bottom: 1rem;

  .selected-info {
    font-weight: 600;
    color: var(--primary-700);
  }

  .bulk-actions {
    display: flex;
    gap: 0.5rem;
  }
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.share-name {
  display: flex;
  align-items: center;

  a {
    color: var(--primary-color);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}

.path-code {
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  background: var(--surface-50);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;

  h3 {
    margin: 1rem 0 0.5rem;
  }

  p {
    color: var(--text-color-secondary);
    margin-bottom: 1.5rem;
  }
}
</style>
```

#### 3.2 Share Form (Create/Edit)

**Components:**
- `ShareFormView.vue` - Main form container with wizard
- `ShareBasicStep.vue` - Step 1: Basic information
- `ShareAccessStep.vue` - Step 2: Access control
- `ShareAdvancedStep.vue` - Step 3: Advanced options
- `ShareReviewStep.vue` - Step 4: Review and confirm

**Features:**
```
Share Creation Wizard (4 Steps)
├── Step 1: Basic Information
│   ├── Share name (validation: no spaces, special chars)
│   ├── File system path (with directory picker)
│   ├── Description/comment
│   ├── Status (Active/Inactive toggle)
│   └── Path validation (exists, permissions check)
├── Step 2: Access Control
│   ├── Permission mode selector
│   │   ├── Read-Only (browseable)
│   │   ├── Read-Write (default)
│   │   └── Custom ACL
│   ├── Valid users (user/group picker with chips)
│   ├── Admin users (elevated permissions)
│   ├── Guest access toggle
│   ├── Browseable toggle
│   └── Preview effective permissions
├── Step 3: Advanced Options
│   ├── Host Allow/Deny (IP ranges, CIDR notation)
│   ├── VFS Objects (audit, recycle bin, etc.)
│   ├── File masks (create mask, directory mask)
│   ├── Case sensitivity options
│   ├── Hide files/dot files options
│   ├── Inherit permissions toggle
│   └── Custom smb.conf parameters (key-value pairs)
└── Step 4: Review & Confirm
    ├── Summary of all settings
    ├── Validation status (all green checks)
    ├── smb.conf preview (generated config)
    ├── Impact warning (if editing existing share)
    └── Create/Save button
```

**PrimeVue Components:**
- `Steps` - Wizard navigation
- `Card` - Step containers
- `InputText`, `Textarea` - Text inputs
- `AutoComplete` - User/group picker with search
- `Chips` - Selected users/groups display
- `InputSwitch` - Boolean toggles
- `RadioButton` - Permission modes
- `Panel` - Collapsible advanced sections
- `Accordion` - Grouped settings
- `Divider` - Section separators
- `Message` - Validation warnings
- `ScrollPanel` - Config preview
- `ConfirmDialog` - Unsaved changes warning

---

### 4. User Management

#### 4.1 User List View

**Components:**
- `UserListView.vue` - Main user list
- `UserQuickFilter.vue` - Quick filters (OU, status, groups)
- `UserBulkImport.vue` - CSV/Excel import dialog
- `UserExportDialog.vue` - Export options

**Features:**
```
User Management
├── User List Display
│   ├── DataTable with all AD attributes
│   ├── Columns: Username, Display Name, Email, OU, Groups, Status, Last Login
│   ├── Avatar/initials for each user
│   ├── Column sorting & filtering
│   ├── Quick filters (sidebar)
│   │   ├── Filter by OU (tree structure)
│   │   ├── Filter by group membership
│   │   ├── Filter by status (enabled/disabled/locked)
│   │   └── Filter by last login (active, inactive >30d, never)
│   └── Saved filter presets
├── Bulk Operations
│   ├── Bulk enable/disable accounts
│   ├── Bulk password reset (force change on next login)
│   ├── Bulk move to OU
│   ├── Bulk add to group
│   ├── Bulk delete (with safeguards)
│   └── Bulk export
├── Import/Export
│   ├── Import from CSV (with template download)
│   ├── Import from Excel
│   ├── Import validation (duplicate check, format check)
│   ├── Import preview (before commit)
│   ├── Export to CSV/Excel/JSON
│   └── Export with group memberships
├── Individual Actions
│   ├── View user details (sidebar)
│   ├── Edit user attributes
│   ├── Reset password
│   ├── Enable/disable account
│   ├── Unlock account
│   ├── Manage group memberships
│   ├── View user's sessions/connections
│   ├── View audit log (user's actions)
│   └── Delete user
└── User Creation
    ├── Single user form
    ├── Template-based creation
    └── Bulk import
```

**PrimeVue Components:**
- `DataTable`, `Column` - User list
- `Avatar` - User avatars
- `Tree` - OU filter tree
- `MultiSelect` - Group filter
- `FileUpload` - CSV/Excel import
- `OverlayPanel` - Quick actions menu
- `Sidebar` - User details panel
- `Chip` - Group badges
- `Tag` - Status indicators
- `Calendar` - Date filters
- `ProgressSpinner` - Import progress

#### 4.2 User Form (Create/Edit)

**Features:**
```
User Form
├── Basic Information Tab
│   ├── Username (sAMAccountName) - auto-generate from name option
│   ├── First Name
│   ├── Last Name
│   ├── Display Name (auto-fill)
│   ├── Email Address
│   ├── Description
│   ├── Organizational Unit (tree selector)
│   └── User Principal Name (UPN)
├── Password Tab
│   ├── Password field (with strength meter)
│   ├── Confirm password
│   ├── Password policy display
│   ├── "User must change password at next login"
│   ├── "Password never expires"
│   ├── "Account is disabled"
│   └── Generate random password button
├── Contact Tab
│   ├── Office
│   ├── Telephone number
│   ├── Mobile phone
│   ├── Fax
│   ├── Street address
│   ├── City, State, ZIP
│   └── Country
├── Groups Tab
│   ├── Current group memberships (with badges)
│   ├── Add to groups (PickList)
│   ├── Primary group selector
│   └── Group details on hover
├── Profile Tab
│   ├── Home directory (auto-create option)
│   ├── Home drive letter
│   ├── Profile path
│   ├── Logon script
│   └── Terminal Services profile
└── Account Tab
    ├── Account expires (calendar picker)
    ├── Logon hours (time grid)
    ├── Logon computers (restrict to specific machines)
    └── Account options checkboxes
```

**PrimeVue Components:**
- `TabView` - Main form tabs
- `InputText` - Text fields
- `Password` - Password fields with meter
- `TreeSelect` - OU selector
- `PickList` - Group membership management
- `Calendar` - Date pickers
- `InputMask` - Phone numbers
- `Panel` - Grouped sections
- `ProgressBar` - Password strength

---

### 5. Group Management

#### 5.1 Group List View

**Features:**
```
Group Management
├── Group List
│   ├── Hierarchical view (groups and nested groups)
│   ├── Flat view (DataTable)
│   ├── Columns: Group Name, Type, Members Count, Description
│   ├── Filter by group type (Security/Distribution)
│   ├── Filter by scope (Global/Domain Local/Universal)
│   └── Search by name/description
├── Bulk Operations
│   ├── Bulk delete groups
│   ├── Bulk add members
│   ├── Bulk export
│   └── Nested group analysis
├── Visualizations
│   ├── Group hierarchy tree (OrganizationChart)
│   ├── Member count chart
│   └── Group relationships diagram
└── Individual Actions
    ├── View group details
    ├── Edit group properties
    ├── Manage members
    ├── View nested groups (recursive)
    ├── Export member list
    └── Delete group
```

**PrimeVue Components:**
- `DataTable` - Flat view
- `Tree` - Hierarchical view
- `OrganizationChart` - Group hierarchy visualization
- `PickList` - Member management
- `Chip` - Member badges
- `Tag` - Group type/scope indicators
- `Chart` - Member statistics

#### 5.2 Group Form

**Features:**
```
Group Form
├── General Tab
│   ├── Group name (cn)
│   ├── sAMAccountName
│   ├── Description
│   ├── Email address (for mail-enabled groups)
│   ├── Group type (Security/Distribution)
│   ├── Group scope (Global/Domain Local/Universal)
│   └── Notes
├── Members Tab
│   ├── Current members list (users and groups)
│   ├── Add members (user/group picker)
│   ├── Remove members
│   ├── Show nested members (recursive)
│   ├── Member type filter (users only, groups only, both)
│   └── Direct vs inherited members
├── Member Of Tab
│   ├── Groups this group belongs to
│   ├── Add to parent groups
│   ├── Remove from groups
│   └── Primary group indicator
└── Managed By Tab
    ├── Manager/owner user picker
    ├── Manager can update membership list
    └── Contact information
```

**PrimeVue Components:**
- `TabView` - Main tabs
- `RadioButton` - Group type/scope
- `DataTable` - Members list
- `AutoComplete` - User/group search
- `TreeTable` - Nested group view
- `InputSwitch` - Boolean options

---

### 6. DNS Management

#### 6.1 DNS Zone Management

**Features:**
```
DNS Zones
├── Zone List
│   ├── Forward lookup zones
│   ├── Reverse lookup zones
│   ├── Zone type (Primary/Secondary/Stub)
│   ├── Dynamic update settings
│   └── Zone status
├── Zone Operations
│   ├── Create new zone
│   ├── Delete zone
│   ├── Reload zone
│   ├── Transfer zone
│   └── Zone properties
└── Zone Details
    ├── SOA record
    ├── Name servers (NS)
    ├── Zone transfers settings
    └── Notify settings
```

#### 6.2 DNS Records Management

**Features:**
```
DNS Records
├── Record Types Support
│   ├── A (IPv4 address)
│   ├── AAAA (IPv6 address)
│   ├── CNAME (Canonical name)
│   ├── MX (Mail exchange)
│   ├── TXT (Text)
│   ├── SRV (Service locator)
│   ├── PTR (Pointer)
│   └── NS (Name server)
├── Record List View
│   ├── DataTable with all records
│   ├── Filter by type
│   ├── Filter by zone
│   ├── Search by name/value
│   └── TTL display
├── Record Operations
│   ├── Create record (type-specific forms)
│   ├── Edit record
│   ├── Delete record
│   ├── Enable/disable record
│   └── Bulk operations
└── Special Features
    ├── Aging/scavenging settings
    ├── Timestamp display (dynamic records)
    ├── Record validation
    └── PTR auto-creation for A records
```

**PrimeVue Components:**
- `DataTable` - Record list
- `Dropdown` - Record type selector
- `InputText` - Name/value fields
- `InputNumber` - TTL, priority, weight
- `TabView` - Record type tabs
- `Message` - Validation warnings
- `Accordion` - Advanced settings

---

### 7. Group Policy Management

#### 7.1 GPO List View

**Features:**
```
Group Policy Objects
├── GPO List
│   ├── All GPOs in domain
│   ├── Status (enabled/disabled/partially enforced)
│   ├── Link status
│   ├── Computer/User settings status
│   ├── WMI filter status
│   └── Last modified timestamp
├── GPO Operations
│   ├── Create new GPO
│   ├── Copy GPO
│   ├── Delete GPO
│   ├── Backup GPO
│   ├── Restore GPO
│   ├── Import settings
│   └── Generate report (HTML/XML)
├── Linking
│   ├── Link to OU
│   ├── Link to domain
│   ├── Link to site
│   ├── Link order management (priority)
│   ├── Enforce option
│   └── Block inheritance
└── Filtering
    ├── Security filtering (users/groups)
    ├── WMI filters
    └── Delegation
```

**PrimeVue Components:**
- `DataTable` - GPO list
- `Tree` - OU structure for linking
- `OrderList` - Link priority management
- `MultiSelect` - Security filtering
- `Panel` - GPO settings sections
- `Tag` - Status indicators
- `Accordion` - Policy categories

#### 7.2 GPO Editor

**Features:**
```
GPO Editor
├── Computer Configuration
│   ├── Software Settings
│   ├── Windows Settings
│   │   ├── Scripts (Startup/Shutdown)
│   │   ├── Security Settings
│   │   └── Registry
│   └── Administrative Templates
│       ├── Windows Components
│       ├── System
│       ├── Network
│       └── Printers
├── User Configuration
│   ├── Software Settings
│   ├── Windows Settings
│   │   ├── Scripts (Logon/Logoff)
│   │   ├── Security Settings
│   │   └── Folder Redirection
│   └── Administrative Templates
│       ├── Windows Components
│       ├── Desktop
│       ├── Start Menu & Taskbar
│       └── Control Panel
├── Policy Editor Features
│   ├── Tree navigation (left sidebar)
│   ├── Policy list (center panel)
│   ├── Policy state (Not Configured/Enabled/Disabled)
│   ├── Policy help text
│   ├── Search policies by name/description
│   ├── Comment/annotation per policy
│   └── Conflict detection
└── Common Policies Quick Access
    ├── Password policy
    ├── Account lockout policy
    ├── User rights assignment
    ├── Security options
    ├── Event log settings
    └── Windows Firewall
```

**PrimeVue Components:**
- `Tree` - Policy navigation
- `DataTable` - Policy list
- `Splitter` - Layout (tree | list | details)
- `SelectButton` - Policy state selector
- `InputText` - Policy values
- `InputNumber` - Numeric policies
- `Checkbox` - Boolean policies
- `TabView` - Computer/User configuration
- `Panel` - Help text
- `Accordion` - Policy categories

---

### 8. Monitoring & Real-time Logs

#### 8.1 Active Connections Monitor

**Features:**
```
Connection Monitoring
├── Live Connection Table
│   ├── Connected user
│   ├── Client IP address
│   ├── Share name
│   ├── Connection time
│   ├── Idle time
│   ├── Open files count
│   ├── Locked files
│   └── Actions (Disconnect, Send message)
├── Real-time Updates (SSE)
│   ├── Auto-refresh every 5 seconds
│   ├── New connection notifications
│   ├── Disconnection notifications
│   └── Connection duration updates
├── Filtering
│   ├── Filter by user
│   ├── Filter by share
│   ├── Filter by client IP/hostname
│   └── Show only idle connections
└── Statistics
    ├── Total active connections
    ├── Peak connections (today)
    ├── Average connection duration
    └── Top users by connection count
```

**PrimeVue Components:**
- `DataTable` - Connections list with auto-refresh
- `Tag` - Status indicators (Active/Idle)
- `Badge` - Open files count
- `Button` - Disconnect action
- `Chart` - Connection trends
- `Timeline` - Connection history

#### 8.2 Open Files Monitor

**Features:**
```
Open Files
├── File List
│   ├── File path
│   ├── User who opened it
│   ├── Access mode (Read/Write)
│   ├── Lock status
│   ├── Open since (timestamp)
│   └── Client machine
├── Operations
│   ├── Close file (force)
│   ├── Send message to user
│   └── View file properties
└── Filtering
    ├── Filter by share
    ├── Filter by user
    ├── Filter by lock status
    └── Show only locked files
```

#### 8.3 Real-time Logs

**Features:**
```
Log Viewer
├── Log Sources
│   ├── Samba logs (smbd, nmbd, winbindd)
│   ├── Application logs (ADHub backend)
│   ├── Authentication logs (LDAP binds)
│   └── Audit logs (administrative actions)
├── Log Display
│   ├── Live log streaming (SSE)
│   ├── Log level filtering (Debug/Info/Warning/Error)
│   ├── Source filtering
│   ├── Text search/highlighting
│   ├── Time range filter
│   └── Export logs
├── Log Levels with Color Coding
│   ├── DEBUG - Gray
│   ├── INFO - Blue
│   ├── WARNING - Orange
│   ├── ERROR - Red
│   └── CRITICAL - Dark Red
└── Features
    ├── Auto-scroll toggle
    ├── Pause/resume streaming
    ├── Line wrapping toggle
    ├── Monospace font
    ├── Copy to clipboard
    └── Download logs
```

**PrimeVue Components:**
- `ScrollPanel` - Log viewer
- `VirtualScroller` - Performance for large logs
- `Chip` - Log level badges
- `MultiSelect` - Source filter
- `InputText` - Search field
- `Calendar` - Time range
- `Button` - Control buttons (pause, export)
- `Tag` - Severity indicators

---

### 9. System Settings

#### 9.1 Samba Configuration

**Features:**
```
Samba Settings
├── Global Settings
│   ├── Workgroup/Domain name
│   ├── NetBIOS name
│   ├── Server string (description)
│   ├── Server role
│   ├── Log level
│   └── Max log size
├── Security Settings
│   ├── Authentication methods
│   ├── Password complexity requirements
│   ├── Password history
│   ├── Account lockout settings
│   ├── Kerberos settings
│   └── LDAP settings
├── Network Settings
│   ├── Interfaces (bind addresses)
│   ├── SMB ports
│   ├── Protocol versions (SMB1/SMB2/SMB3)
│   └── Client signing requirements
└── File Settings
    ├── Default file permissions
    ├── Default directory permissions
    ├── Case sensitivity
    ├── Preserve case
    └── Short names (8.3 format)
```

#### 9.2 Application Settings

**Features:**
```
Application Configuration
├── Authentication
│   ├── LDAP server address
│   ├── LDAP port (636 for LDAPS)
│   ├── Base DN
│   ├── Bind credentials (for service account)
│   ├── LDAP timeout settings
│   └── Role mapping configuration
├── Database
│   ├── Connection pool settings
│   ├── Query timeout
│   ├── Backup schedule
│   └── Retention policy
├── Cache & Session
│   ├── Redis connection settings
│   ├── Session timeout
│   ├── Cache TTL settings
│   └── Cache size limits
├── Notifications
│   ├── Email server (SMTP)
│   ├── Email from address
│   ├── Admin notification settings
│   ├── User notification settings
│   └── Alert thresholds
└── UI Settings
    ├── Default theme
    ├── Date/time format
    ├── Default page sizes
    ├── Auto-refresh intervals
    └── Dashboard widgets configuration
```

**PrimeVue Components:**
- `TabView` - Settings categories
- `InputText` - Text settings
- `InputNumber` - Numeric settings
- `Dropdown` - Selection settings
- `InputSwitch` - Boolean toggles
- `Password` - Credentials
- `Chip` - Multi-value settings
- `Message` - Validation/info messages
- `Panel` - Grouped settings

#### 9.3 Backup & Restore

**Features:**
```
Backup & Restore
├── Manual Backup
│   ├── Full system backup
│   ├── Samba configuration only
│   ├── AD database
│   ├── GPO backup
│   └── Application database
├── Scheduled Backups
│   ├── Schedule configuration (cron-like)
│   ├── Backup retention policy
│   ├── Backup destination
│   └── Compression settings
├── Restore
│   ├── List available backups
│   ├── Backup details (size, date, contents)
│   ├── Selective restore
│   ├── Full restore
│   └── Restore preview (what will change)
└── Backup History
    ├── Backup list with status
    ├── Size and duration
    ├── Success/failure logs
    └── Download backup file
```

**PrimeVue Components:**
- `DataTable` - Backup list
- `Calendar` - Schedule picker
- `InputNumber` - Retention days
- `SelectButton` - Backup type
- `ProgressBar` - Backup/restore progress
- `FileUpload` - Restore from file
- `Timeline` - Backup history

---

### 10. Audit & Reports

#### 10.1 Audit Log

**Features:**
```
Audit Logging
├── Audit Events
│   ├── User actions (create, edit, delete)
│   ├── Group modifications
│   ├── Share changes
│   ├── GPO changes
│   ├── DNS record changes
│   ├── System setting changes
│   ├── Login attempts (success/failure)
│   └── Permission changes
├── Audit Log View
│   ├── DataTable with all events
│   ├── Columns: Timestamp, User, Action, Target, Result, IP Address
│   ├── Filter by date range
│   ├── Filter by user
│   ├── Filter by action type
│   ├── Filter by result (success/failure)
│   └── Full-text search
├── Export & Reporting
│   ├── Export to CSV/Excel
│   ├── Generate PDF report
│   ├── Schedule automated reports
│   └── Email reports
└── Compliance
    ├── Compliance dashboard (SOX, HIPAA, etc.)
    ├── Failed login report
    ├── Permission changes report
    ├── Privileged access report
    └── Retention policy enforcement
```

**PrimeVue Components:**
- `DataTable` - Audit log list
- `Calendar` - Date range picker
- `MultiSelect` - Event type filter
- `Timeline` - Event chronology view
- `Tag` - Result indicators (Success/Failure)
- `Button` - Export actions

#### 10.2 Reports & Analytics

**Features:**
```
Reports
├── Pre-built Reports
│   ├── User Account Report
│   │   ├── All users
│   │   ├── Inactive users (>30/60/90 days)
│   │   ├── Disabled accounts
│   │   ├── Password expiring soon
│   │   └── Never logged in
│   ├── Group Membership Report
│   │   ├── Group member list
│   │   ├── Nested group analysis
│   │   ├── Users with multiple groups
│   │   └── Empty groups
│   ├── Share Usage Report
│   │   ├── Most accessed shares
│   │   ├── Inactive shares
│   │   ├── Share permissions summary
│   │   └── Disk usage by share
│   ├── Security Report
│   │   ├── Failed login attempts
│   │   ├── Account lockouts
│   │   ├── Permission changes
│   │   └── Privileged access log
│   └── GPO Report
│       ├── GPO application status
│       ├── GPO settings report
│       └── Unlinked GPOs
├── Custom Reports
│   ├── Report builder interface
│   ├── Query builder (visual)
│   ├── Field selection
│   ├── Filter configuration
│   └── Save report templates
└── Dashboards
    ├── Executive dashboard (high-level metrics)
    ├── Security dashboard (threats, anomalies)
    ├── Capacity dashboard (storage, users)
    └── Performance dashboard (connection stats)
```

**PrimeVue Components:**
- `Chart` - Various chart types (Line, Bar, Pie, Doughnut)
- `DataTable` - Report data
- `Calendar` - Date range selection
- `Dropdown` - Report type selector
- `Button` - Export/schedule buttons
- `Card` - Dashboard widgets
- `Knob` - Gauge charts
- `ProgressBar` - Capacity indicators

---

## 11. Backend Service Layer Structure

### 11.1 Samba Integration Wrapper

**Module:** `app/services/samba/`

```
samba/
├── __init__.py
├── client.py              # Main Samba client wrapper
├── users.py               # User management operations
├── groups.py              # Group management operations
├── shares.py              # Share management operations
├── dns.py                 # DNS operations
├── gpo.py                 # Group Policy operations
├── monitoring.py          # Monitoring (connections, files, etc.)
├── exceptions.py          # Custom exceptions
└── utils.py               # Helper functions
```

**Key Classes:**

```python
# app/services/samba/client.py
class SambaClient:
    """Main Samba client using python-samba bindings"""

    def __init__(self, config: SambaConfig):
        self.lp = LoadParm()
        self.creds = Credentials()
        self.samdb = None

    async def connect(self):
        """Establish connection to Samba"""

    async def disconnect(self):
        """Close connection"""

    @property
    def sam_db(self) -> SamDB:
        """Get SAM database connection"""

# app/services/samba/users.py
class UserService:
    """AD user management using python-samba"""

    def __init__(self, client: SambaClient):
        self.client = client

    async def create_user(self, user_data: UserCreate) -> User:
        """Create new AD user"""

    async def get_user(self, username: str) -> User:
        """Get user by username"""

    async def update_user(self, username: str, updates: UserUpdate) -> User:
        """Update user attributes"""

    async def delete_user(self, username: str):
        """Delete user"""

    async def reset_password(self, username: str, new_password: str):
        """Reset user password"""

    async def enable_user(self, username: str):
        """Enable user account"""

    async def disable_user(self, username: str):
        """Disable user account"""

    async def list_users(self, filters: dict = None) -> List[User]:
        """List all users with optional filters"""
```

### 11.2 LDAP Authentication Service

```python
# app/services/auth/ldap_auth.py
class LDAPAuthService:
    """LDAP authentication against Samba AD"""

    def __init__(self, config: LDAPConfig):
        self.server_uri = config.server_uri
        self.base_dn = config.base_dn

    async def authenticate(
        self,
        username: str,
        password: str
    ) -> Tuple[bool, Optional[LDAPUser]]:
        """
        Authenticate user via LDAP bind
        Returns: (success: bool, user_info: LDAPUser | None)
        """
        try:
            # Construct user DN
            user_dn = f"cn={username},{self.base_dn}"

            # Attempt LDAP bind with credentials
            server = Server(self.server_uri, use_ssl=True)
            conn = Connection(
                server,
                user=user_dn,
                password=password,
                auto_bind=True
            )

            if not conn.bind():
                return False, None

            # Fetch user attributes
            user_info = await self._get_user_info(conn, user_dn)

            # Map AD groups to application roles
            roles = await self._map_groups_to_roles(user_info.groups)
            user_info.roles = roles

            conn.unbind()
            return True, user_info

        except Exception as e:
            logger.error(f"LDAP auth failed: {e}")
            return False, None

    async def _map_groups_to_roles(
        self,
        ad_groups: List[str]
    ) -> List[str]:
        """Map AD groups to application roles"""
        role_mappings = await get_role_mappings()

        roles = []
        for mapping in role_mappings:
            if mapping.ad_group_dn in ad_groups:
                roles.append(mapping.role_name)

        return roles
```

### 11.3 Real-time Updates (SSE)

```python
# app/api/sse.py
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

router = APIRouter()

@router.get("/events/connections")
async def stream_connections(
    current_user: User = Depends(get_current_user)
):
    """Stream active connection updates via SSE"""

    async def event_generator():
        while True:
            # Fetch current connections from Samba
            connections = await monitoring_service.get_connections()

            # Yield as SSE event
            yield {
                "event": "connection_update",
                "data": json.dumps({
                    "connections": connections,
                    "timestamp": datetime.now().isoformat()
                })
            }

            # Wait before next update
            await asyncio.sleep(5)

    return EventSourceResponse(event_generator())


@router.get("/events/logs")
async def stream_logs(
    level: Optional[str] = None,
    source: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Stream log entries via SSE"""

    async def event_generator():
        # Tail log files and stream new entries
        async for log_entry in log_service.tail_logs(level, source):
            yield {
                "event": "log_entry",
                "data": json.dumps(log_entry.dict())
            }

    return EventSourceResponse(event_generator())
```

---

## 12. Frontend Architecture Patterns

### 12.1 Pinia Store Pattern

```typescript
// stores/share.ts
import { defineStore } from 'pinia'
import type { Share, ShareCreate, ShareUpdate } from '@/types/share'
import { shareApi } from '@/api/shares'

export const useShareStore = defineStore('share', {
  state: () => ({
    shares: [] as Share[],
    currentShare: null as Share | null,
    loading: false,
    error: null as string | null,
    totalCount: 0,
    filters: {},
    sort: {}
  }),

  getters: {
    activeShares: (state) => state.shares.filter(s => s.status === 'Active'),

    getShareById: (state) => (id: string) =>
      state.shares.find(s => s.id === id),

    sortedShares: (state) => {
      // Apply sorting logic
      return [...state.shares].sort((a, b) => {
        // Sort implementation
      })
    }
  },

  actions: {
    async fetchShares(params = {}) {
      this.loading = true
      this.error = null

      try {
        const response = await shareApi.list(params)
        this.shares = response.data
        this.totalCount = response.total
      } catch (error: any) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async createShare(data: ShareCreate) {
      this.loading = true
      try {
        const share = await shareApi.create(data)
        this.shares.push(share)
        return share
      } catch (error: any) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateShare(id: string, data: ShareUpdate) {
      this.loading = true
      try {
        const share = await shareApi.update(id, data)
        const index = this.shares.findIndex(s => s.id === id)
        if (index !== -1) {
          this.shares[index] = share
        }
        return share
      } catch (error: any) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteShare(id: string) {
      this.loading = true
      try {
        await shareApi.delete(id)
        this.shares = this.shares.filter(s => s.id !== id)
      } catch (error: any) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
```

### 12.2 API Client Pattern

```typescript
// api/client.ts
import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore()
        if (authStore.accessToken) {
          config.headers.Authorization = `Bearer ${authStore.accessToken}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        // Handle 401 Unauthorized - try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          const authStore = useAuthStore()
          const refreshed = await authStore.refreshAccessToken()

          if (refreshed) {
            return this.client(originalRequest)
          } else {
            router.push('/login')
          }
        }

        // Handle other errors
        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config)
    return response.data
  }
}

export const apiClient = new ApiClient()

// api/shares.ts
import { apiClient } from './client'
import type { Share, ShareCreate, ShareUpdate, PaginatedResponse } from '@/types'

export const shareApi = {
  list: (params = {}) =>
    apiClient.get<PaginatedResponse<Share>>('/shares', { params }),

  get: (id: string) =>
    apiClient.get<Share>(`/shares/${id}`),

  create: (data: ShareCreate) =>
    apiClient.post<Share>('/shares', data),

  update: (id: string, data: ShareUpdate) =>
    apiClient.put<Share>(`/shares/${id}`, data),

  delete: (id: string) =>
    apiClient.delete<void>(`/shares/${id}`),

  duplicate: (id: string) =>
    apiClient.post<Share>(`/shares/${id}/duplicate`)
}
```

### 12.3 Composables Pattern

```typescript
// composables/usePagination.ts
import { ref, computed } from 'vue'

export function usePagination(initialPageSize = 25) {
  const page = ref(0)
  const pageSize = ref(initialPageSize)
  const totalRecords = ref(0)

  const offset = computed(() => page.value * pageSize.value)
  const totalPages = computed(() => Math.ceil(totalRecords.value / pageSize.value))

  const onPage = (event: any) => {
    page.value = event.page
    pageSize.value = event.rows
  }

  const reset = () => {
    page.value = 0
  }

  return {
    page,
    pageSize,
    totalRecords,
    offset,
    totalPages,
    onPage,
    reset
  }
}

// composables/useDataTable.ts
import { ref, reactive } from 'vue'
import { FilterMatchMode } from 'primevue/api'

export function useDataTable() {
  const loading = ref(false)
  const selectedItems = ref([])

  const filters = reactive({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS }
  })

  const clearSelection = () => {
    selectedItems.value = []
  }

  const clearFilters = () => {
    Object.keys(filters).forEach(key => {
      filters[key].value = null
    })
  }

  return {
    loading,
    selectedItems,
    filters,
    clearSelection,
    clearFilters
  }
}
```

---

## 13. Testing Strategy

### 13.1 Backend Tests

```python
# tests/test_users.py
import pytest
from app.services.samba.users import UserService

@pytest.mark.asyncio
async def test_create_user(samba_client, user_data):
    """Test user creation"""
    service = UserService(samba_client)

    user = await service.create_user(user_data)

    assert user.username == user_data.username
    assert user.email == user_data.email

@pytest.mark.asyncio
async def test_authenticate_valid_user(ldap_auth_service):
    """Test LDAP authentication with valid credentials"""
    success, user_info = await ldap_auth_service.authenticate(
        "testuser",
        "ValidPassword123"
    )

    assert success is True
    assert user_info is not None
    assert user_info.username == "testuser"
```

### 13.2 Frontend Tests

```typescript
// tests/components/ShareListView.spec.ts
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import ShareListView from '@/views/shares/ShareListView.vue'

describe('ShareListView', () => {
  it('renders share list', async () => {
    const wrapper = mount(ShareListView, {
      global: {
        plugins: [createTestingPinia()]
      }
    })

    expect(wrapper.find('h1').text()).toBe('SMB Shares')
  })

  it('loads shares on mount', async () => {
    const wrapper = mount(ShareListView, {
      global: {
        plugins: [createTestingPinia({
          stubActions: false
        })]
      }
    })

    // Assert shares were loaded
    expect(wrapper.vm.shares.length).toBeGreaterThan(0)
  })
})
```

---

## 14. Deployment Configuration

### 14.1 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://adhub:password@db:5432/adhub
      - REDIS_URL=redis://redis:6379/0
      - LDAP_SERVER=ldap://samba-dc:636
    volumes:
      - ./backend:/app
      - /etc/samba:/etc/samba:ro
    depends_on:
      - db
      - redis
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./frontend/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=adhub
      - POSTGRES_USER=adhub
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.celery worker -l info
    environment:
      - DATABASE_URL=postgresql://adhub:password@db:5432/adhub
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - db
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

---

## Summary

This technical specification provides implementation-level details for ADHub with:

✅ **Complete library lists** for frontend (PrimeVue ecosystem) and backend (Python/FastAPI)
✅ **Detailed feature breakdowns** for all major modules
✅ **Specific PrimeVue components** mapped to each feature
✅ **Full Vue 3 component implementations** with TypeScript
✅ **Backend service layer architecture** with Samba integration
✅ **LDAP authentication** implementation
✅ **Real-time features** using SSE
✅ **Testing strategy** for both frontend and backend
✅ **Deployment configuration** with Docker Compose

All features use **PrimeVue 3.48+** as the primary UI framework with its complete ecosystem of 90+ components, providing a consistent, professional interface for managing Samba infrastructure.
