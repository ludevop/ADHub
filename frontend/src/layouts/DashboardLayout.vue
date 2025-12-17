<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const showUserMenu = ref(false)
const sidebarCollapsed = ref(false)

const displayName = computed(() => {
  return authStore.user?.display_name || authStore.user?.username || 'User'
})

const userInitials = computed(() => {
  const name = displayName.value
  const parts = name.split(' ').filter(p => p.length > 0)
  if (parts.length >= 2) {
    const firstChar = parts[0]?.charAt(0) || ''
    const secondChar = parts[1]?.charAt(0) || ''
    if (firstChar && secondChar) {
      return (firstChar + secondChar).toUpperCase()
    }
  }
  return name.substring(0, Math.min(2, name.length)).toUpperCase()
})

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}

function closeUserMenu() {
  showUserMenu.value = false
}

// Navigation items
const navItems = [
  { name: 'Dashboard', icon: '📊', path: '/dashboard' },
  { name: 'Users', icon: '👥', path: '/dashboard/users', disabled: true },
  { name: 'Groups', icon: '👨‍👩‍👧‍👦', path: '/dashboard/groups', disabled: true },
  { name: 'Shares', icon: '📁', path: '/dashboard/shares', disabled: true },
  { name: 'DNS', icon: '🌐', path: '/dashboard/dns', disabled: true },
  { name: 'Group Policy', icon: '📋', path: '/dashboard/gpo', disabled: true },
  { name: 'Settings', icon: '⚙️', path: '/dashboard/settings', disabled: true }
]
</script>

<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <h1 class="logo">ADHub</h1>
        <button
          class="collapse-btn"
          @click="sidebarCollapsed = !sidebarCollapsed"
          :title="sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        >
          {{ sidebarCollapsed ? '→' : '←' }}
        </button>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ disabled: item.disabled }"
          @click="item.disabled && $event.preventDefault()"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span v-if="!sidebarCollapsed" class="nav-label">{{ item.name }}</span>
          <span v-if="item.disabled && !sidebarCollapsed" class="badge">Soon</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="domain-info" v-if="!sidebarCollapsed && authStore.user">
          <div class="domain-label">Domain</div>
          <div class="domain-name">{{ authStore.user.domain }}</div>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <div class="main-content">
      <!-- Top bar -->
      <header class="top-bar">
        <div class="top-bar-left">
          <h2 class="page-title">{{ $route.meta.title || 'Dashboard' }}</h2>
        </div>

        <div class="top-bar-right">
          <!-- User menu -->
          <div class="user-menu-container" @click.stop>
            <button class="user-menu-trigger" @click="toggleUserMenu">
              <div class="user-avatar">{{ userInitials }}</div>
              <div class="user-info">
                <div class="user-name">{{ displayName }}</div>
                <div class="user-role">{{ authStore.isAdmin ? 'Administrator' : 'User' }}</div>
              </div>
              <span class="dropdown-arrow">▼</span>
            </button>

            <div v-if="showUserMenu" class="user-menu-dropdown" @click.stop>
              <div class="user-menu-header">
                <div class="user-menu-name">{{ displayName }}</div>
                <div class="user-menu-email">{{ authStore.user?.email || authStore.user?.username }}</div>
              </div>

              <div class="user-menu-divider"></div>

              <button class="user-menu-item" disabled>
                <span class="menu-icon">👤</span>
                Profile
                <span class="badge">Soon</span>
              </button>

              <button class="user-menu-item" disabled>
                <span class="menu-icon">⚙️</span>
                Settings
                <span class="badge">Soon</span>
              </button>

              <div class="user-menu-divider"></div>

              <button class="user-menu-item logout" @click="handleLogout">
                <span class="menu-icon">🚪</span>
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="page-content">
        <router-view />
      </main>
    </div>

    <!-- Click outside to close user menu -->
    <div v-if="showUserMenu" class="overlay" @click="closeUserMenu"></div>
  </div>
</template>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
}

/* Sidebar */
.sidebar {
  width: 260px;
  background: #2c3e50;
  color: white;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: fixed;
  height: 100vh;
  z-index: 100;
}

.sidebar.collapsed {
  width: 70px;
}

.sidebar-header {
  padding: 1.5rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar.collapsed .logo {
  font-size: 1.2rem;
}

.collapse-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.2s;
  position: relative;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 0.875rem 0.5rem;
}

.nav-item:hover:not(.disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.router-link-active:not(.disabled) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.nav-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.nav-label {
  flex: 1;
  white-space: nowrap;
}

.badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.domain-info {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.75rem;
  border-radius: 8px;
}

.domain-label {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-bottom: 0.25rem;
}

.domain-name {
  font-weight: 600;
  font-size: 0.875rem;
}

/* Main content */
.main-content {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
}

.sidebar.collapsed ~ .main-content {
  margin-left: 70px;
}

.top-bar {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.page-title {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
  font-weight: 600;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* User menu */
.user-menu-container {
  position: relative;
}

.user-menu-trigger {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.2s;
}

.user-menu-trigger:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.user-info {
  text-align: left;
}

.user-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: #2c3e50;
}

.user-role {
  font-size: 0.75rem;
  color: #7f8c8d;
}

.dropdown-arrow {
  font-size: 0.625rem;
  color: #7f8c8d;
  margin-left: 0.5rem;
}

.user-menu-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  min-width: 240px;
  z-index: 1000;
}

.user-menu-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e0e0e0;
}

.user-menu-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.user-menu-email {
  font-size: 0.875rem;
  color: #7f8c8d;
}

.user-menu-divider {
  height: 1px;
  background: #e0e0e0;
  margin: 0.5rem 0;
}

.user-menu-item {
  width: 100%;
  padding: 0.75rem 1.25rem;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #2c3e50;
  transition: background 0.2s;
  font-size: 0.9375rem;
}

.user-menu-item:hover:not(:disabled) {
  background: #f5f7fa;
}

.user-menu-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.user-menu-item.logout {
  color: #e74c3c;
}

.user-menu-item.logout:hover {
  background: #fee;
}

.menu-icon {
  font-size: 1.125rem;
}

.page-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    width: 70px;
  }

  .main-content {
    margin-left: 70px;
  }

  .top-bar {
    padding: 1rem;
  }

  .page-content {
    padding: 1rem;
  }

  .user-info {
    display: none;
  }
}
</style>
