<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSetupStore } from '@/stores/setup'
import { DomainFunctionLevel } from '@/types/setup'

const setupStore = useSetupStore()
const config = setupStore.domainConfig
const confirmPassword = ref('')

const passwordsMatch = computed(() => {
  return config.admin_password === confirmPassword.value
})

const isValid = computed(() => {
  return (
    config.realm.length > 0 &&
    config.domain.length > 0 &&
    config.domain_name.length > 0 &&
    config.admin_password.length >= 8 &&
    passwordsMatch.value
  )
})

function autofillFromDomain() {
  if (config.domain_name) {
    config.realm = config.domain_name.toUpperCase()
    const parts = config.domain_name.split('.')
    config.domain = (parts[0] || config.domain_name).toUpperCase()
  }
}
</script>

<template>
  <div class="domain-config-step">
    <h2>Domain Configuration</h2>
    <p class="description">Configure your Active Directory domain settings.</p>

    <div class="form-container">
      <div class="form-group">
        <label for="domain_name">
          DNS Domain Name
          <span class="required">*</span>
        </label>
        <input
          id="domain_name"
          v-model="config.domain_name"
          type="text"
          placeholder="example.com"
          @blur="autofillFromDomain"
        />
        <small>Fully qualified domain name (e.g., example.com)</small>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="realm">
            Kerberos Realm
            <span class="required">*</span>
          </label>
          <input
            id="realm"
            v-model="config.realm"
            type="text"
            placeholder="EXAMPLE.COM"
            style="text-transform: uppercase"
          />
          <small>Usually matches domain name in UPPERCASE</small>
        </div>

        <div class="form-group">
          <label for="domain">
            NetBIOS Domain Name
            <span class="required">*</span>
          </label>
          <input
            id="domain"
            v-model="config.domain"
            type="text"
            placeholder="EXAMPLE"
            maxlength="15"
            style="text-transform: uppercase"
          />
          <small>Max 15 characters, UPPERCASE</small>
        </div>
      </div>

      <div class="form-group">
        <label for="function_level">Domain Functional Level</label>
        <select id="function_level" v-model="config.function_level">
          <option :value="DomainFunctionLevel.LEVEL_2008">
            Windows Server 2008 (Recommended)
          </option>
          <option :value="DomainFunctionLevel.LEVEL_2008_R2">
            Windows Server 2008 R2
          </option>
          <option :value="DomainFunctionLevel.LEVEL_2003">
            Windows Server 2003
          </option>
          <option :value="DomainFunctionLevel.LEVEL_2000">
            Windows 2000 (Legacy)
          </option>
        </select>
        <small>Windows Server 2008 is recommended for maximum compatibility with Samba 4.x.</small>
      </div>

      <div class="divider"></div>

      <h3>Administrator Account</h3>

      <div class="form-group">
        <label for="admin_password">
          Administrator Password
          <span class="required">*</span>
        </label>
        <input
          id="admin_password"
          v-model="config.admin_password"
          type="password"
          placeholder="Strong password"
        />
        <small>Minimum 8 characters with uppercase, lowercase, and numbers</small>
      </div>

      <div class="form-group">
        <label for="confirm_password">
          Confirm Password
          <span class="required">*</span>
        </label>
        <input
          id="confirm_password"
          v-model="confirmPassword"
          type="password"
          placeholder="Repeat password"
        />
        <small v-if="confirmPassword && !passwordsMatch" class="error">Passwords do not match</small>
        <small v-else-if="confirmPassword && passwordsMatch" class="success">Passwords match ✓</small>
      </div>

      <div class="info-box">
        <h4>💡 Tips</h4>
        <ul>
          <li>Choose a domain name you control (e.g., internal.example.com)</li>
          <li>Use UPPERCASE for Realm and NetBIOS domain</li>
          <li>Administrator password should be very strong</li>
          <li>Store credentials safely - you'll need them later</li>
        </ul>
      </div>
    </div>

    <div class="button-group">
      <button @click="setupStore.previousStep()" class="btn btn-secondary">← Back</button>
      <button @click="setupStore.nextStep()" class="btn btn-primary" :disabled="!isValid">
        Continue →
      </button>
    </div>
  </div>
</template>

<style scoped>
.domain-config-step {
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

.form-container {
  display: grid;
  gap: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: grid;
  gap: 0.5rem;
}

label {
  font-weight: 600;
  color: #2c3e50;
}

.required {
  color: #e74c3c;
}

input,
select {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus,
select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

small {
  color: #7f8c8d;
  font-size: 0.85rem;
}

small.error {
  color: #e74c3c;
}

small.success {
  color: #2ecc71;
}

.divider {
  border-top: 1px solid #e0e0e0;
  margin: 1rem 0;
}

h3 {
  color: #2c3e50;
  margin: 0;
}

.info-box {
  background: #e8f4f8;
  border-left: 4px solid #3498db;
  padding: 1rem;
  border-radius: 4px;
}

.info-box h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.info-box ul {
  margin: 0;
  padding-left: 1.5rem;
}

.info-box li {
  margin: 0.25rem 0;
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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
