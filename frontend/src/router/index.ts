// Vue Router configuration

import { createRouter, createWebHistory } from 'vue-router'
import SetupWizard from '@/views/SetupWizard.vue'
import Login from '@/views/Login.vue'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import DashboardHome from '@/views/dashboard/Home.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: () => {
        // Will be handled by navigation guard
        return '/setup'
      }
    },
    {
      path: '/setup',
      name: 'setup',
      component: SetupWizard,
      meta: { requiresNoAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { requiresNoAuth: true }
    },
    {
      path: '/dashboard',
      component: DashboardLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: DashboardHome
        }
      ]
    }
  ]
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Initialize auth store on first navigation
  if (!authStore.setupStatus) {
    await authStore.initialize()
  }

  const isAuthenticated = authStore.isAuthenticated
  const setupCompleted = authStore.setupCompleted
  const canSkipToDashboard = authStore.canSkipToDashboard

  // If trying to access root, redirect based on state
  if (to.path === '/') {
    if (!setupCompleted) {
      return next('/setup')
    } else if (!isAuthenticated) {
      return next('/login')
    } else {
      return next('/dashboard')
    }
  }

  // If setup is not completed and not going to setup, redirect to setup
  if (!setupCompleted && to.path !== '/setup') {
    return next('/setup')
  }

  // If setup is completed and going to setup, redirect based on auth
  if (setupCompleted && to.path === '/setup') {
    if (isAuthenticated) {
      return next('/dashboard')
    } else {
      return next('/login')
    }
  }

  // Handle routes that require authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login')
  }

  // Handle routes that require no authentication (login, setup)
  if (to.meta.requiresNoAuth && isAuthenticated && to.path === '/login') {
    return next('/dashboard')
  }

  next()
})

export default router
