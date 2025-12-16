// Vue Router configuration

import { createRouter, createWebHistory } from 'vue-router'
import SetupWizard from '@/views/SetupWizard.vue'
import Dashboard from '@/views/Dashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/setup'
    },
    {
      path: '/setup',
      name: 'setup',
      component: SetupWizard
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard
    }
  ]
})

export default router
