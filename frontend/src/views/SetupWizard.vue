<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useSetupStore } from '@/stores/setup'
import { SetupStep } from '@/types/setup'

// Step components
import WelcomeStep from '@/components/setup/WelcomeStep.vue'
import PrerequisitesStep from '@/components/setup/PrerequisitesStep.vue'
import DomainConfigStep from '@/components/setup/DomainConfigStep.vue'
import DNSConfigStep from '@/components/setup/DNSConfigStep.vue'
import ReviewStep from '@/components/setup/ReviewStep.vue'
import ProvisionStep from '@/components/setup/ProvisionStep.vue'
import VerificationStep from '@/components/setup/VerificationStep.vue'
import CompleteStep from '@/components/setup/CompleteStep.vue'
import ExistingDomainModal from '@/components/setup/ExistingDomainModal.vue'

const setupStore = useSetupStore()
const showExistingDomainModal = ref(false)

const stepTitles = [
  'Welcome',
  'Prerequisites',
  'Domain Configuration',
  'DNS Configuration',
  'Review',
  'Provision',
  'Verification',
  'Complete'
]

const currentStepComponent = computed(() => {
  const components = [
    WelcomeStep,
    PrerequisitesStep,
    DomainConfigStep,
    DNSConfigStep,
    ReviewStep,
    ProvisionStep,
    VerificationStep,
    CompleteStep
  ]
  return components[setupStore.currentStep]
})

const progressPercentage = computed(() => {
  return ((setupStore.currentStep + 1) / stepTitles.length) * 100
})

onMounted(async () => {
  await setupStore.checkStatus()

  // Show modal if domain is already provisioned and we're on step 0
  if (setupStore.isProvisioned && setupStore.currentStep === 0) {
    showExistingDomainModal.value = true
  }
})

function closeModal() {
  showExistingDomainModal.value = false
}
</script>

<template>
  <div class="setup-wizard">
    <header class="wizard-header">
      <h1>🚀 Samba AD Domain Controller Setup</h1>
      <p class="subtitle">Configure your Active Directory environment</p>

      <!-- Existing domain banner -->
      <div v-if="setupStore.isProvisioned && setupStore.currentStep < 6" class="existing-domain-banner">
        <div class="banner-content">
          <span class="banner-icon">⚠️</span>
          <span class="banner-text">An existing domain configuration was detected</span>
          <button @click="showExistingDomainModal = true" class="banner-button">
            View Options
          </button>
        </div>
      </div>
    </header>

    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
    </div>

    <div class="wizard-steps">
      <div
        v-for="(title, index) in stepTitles"
        :key="index"
        :class="['step-indicator', { active: index === setupStore.currentStep, completed: index < setupStore.currentStep }]"
      >
        <div class="step-number">{{ index + 1 }}</div>
        <div class="step-title">{{ title }}</div>
      </div>
    </div>

    <div class="wizard-content">
      <component :is="currentStepComponent" @showExistingDomainModal="showExistingDomainModal = true" />
    </div>

    <!-- Existing domain modal -->
    <ExistingDomainModal v-if="showExistingDomainModal" @close="closeModal" />
  </div>
</template>

<style scoped>
.setup-wizard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.wizard-header {
  text-align: center;
  margin-bottom: 2rem;
}

.wizard-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.1rem;
  color: #7f8c8d;
  margin-bottom: 1rem;
}

.existing-domain-banner {
  margin-top: 1rem;
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  border: 2px solid #e67e22;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(230, 126, 34, 0.2);
}

.banner-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.banner-icon {
  font-size: 1.5rem;
}

.banner-text {
  font-weight: 600;
  color: #856404;
  font-size: 1rem;
}

.banner-button {
  padding: 0.5rem 1.25rem;
  background: #e67e22;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.banner-button:hover {
  background: #d35400;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(230, 126, 34, 0.3);
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 2rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.3s ease;
}

.wizard-steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 3rem;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  opacity: 0.5;
  transition: opacity 0.3s;
}

.step-indicator.active,
.step-indicator.completed {
  opacity: 1;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: all 0.3s;
}

.step-indicator.active .step-number {
  background: #3498db;
  color: white;
  transform: scale(1.1);
}

.step-indicator.completed .step-number {
  background: #2ecc71;
  color: white;
}

.step-title {
  font-size: 0.85rem;
  text-align: center;
  max-width: 100px;
}

.wizard-content {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-height: 400px;
}

@media (max-width: 768px) {
  .wizard-steps {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
  }

  .step-title {
    font-size: 0.75rem;
  }
}
</style>
