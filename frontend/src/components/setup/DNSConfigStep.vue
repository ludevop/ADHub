<script setup lang="ts">
import { useSetupStore } from '@/stores/setup'
import { DNSBackendType } from '@/types/setup'

const setupStore = useSetupStore()
const config = setupStore.domainConfig
</script>

<template>
  <div class="dns-config-step">
    <h2>DNS Configuration</h2>
    <p class="description">Configure DNS settings for your Active Directory domain.</p>

    <div class="form-container">
      <div class="form-group">
        <label for="dns_backend">DNS Backend</label>
        <select id="dns_backend" v-model="config.dns_backend">
          <option :value="DNSBackendType.SAMBA_INTERNAL">
            SAMBA_INTERNAL (Recommended for most setups)
          </option>
          <option :value="DNSBackendType.BIND9_DLZ">BIND9_DLZ (Advanced)</option>
          <option :value="DNSBackendType.NONE">NONE (External DNS)</option>
        </select>
        <small>SAMBA_INTERNAL is recommended unless you have specific requirements</small>
      </div>

      <div v-if="config.dns_backend !== DNSBackendType.NONE" class="form-group">
        <label for="dns_forwarder">DNS Forwarder</label>
        <input
          id="dns_forwarder"
          v-model="config.dns_forwarder"
          type="text"
          placeholder="8.8.8.8"
        />
        <small>External DNS server to forward queries (e.g., 8.8.8.8, 1.1.1.1)</small>
      </div>

      <div class="form-group">
        <label for="host_ip">Host IP Address (Optional)</label>
        <input
          id="host_ip"
          v-model="config.host_ip"
          type="text"
          placeholder="192.168.1.10"
        />
        <small>Leave empty to auto-detect, or specify static IP</small>
      </div>

      <div class="info-box">
        <h4>📝 DNS Backend Options</h4>
        <div class="backend-info">
          <div>
            <strong>SAMBA_INTERNAL:</strong>
            <p>Built-in DNS server, easiest to configure. Recommended for most users.</p>
          </div>
          <div>
            <strong>BIND9_DLZ:</strong>
            <p>Use BIND9 as DNS server with DLZ plugin. For advanced users who need BIND features.</p>
          </div>
          <div>
            <strong>NONE:</strong>
            <p>No DNS server. Use this if you're configuring external DNS manually.</p>
          </div>
        </div>
      </div>

      <div class="warning-box">
        <h4>⚠️ Important Notes</h4>
        <ul>
          <li>DNS is critical for Active Directory functionality</li>
          <li>Make sure DNS forwarder is reachable from your network</li>
          <li>Using a static IP is highly recommended for domain controllers</li>
          <li>Client machines will need to use this DC as their DNS server</li>
        </ul>
      </div>
    </div>

    <div class="button-group">
      <button @click="setupStore.previousStep()" class="btn btn-secondary">← Back</button>
      <button @click="setupStore.nextStep()" class="btn btn-primary">Continue →</button>
    </div>
  </div>
</template>

<style scoped>
.dns-config-step {
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

.form-group {
  display: grid;
  gap: 0.5rem;
}

label {
  font-weight: 600;
  color: #2c3e50;
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

.info-box,
.warning-box {
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid;
}

.info-box {
  background: #e8f4f8;
  border-color: #3498db;
}

.warning-box {
  background: #fff3cd;
  border-color: #f39c12;
}

.info-box h4,
.warning-box h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.backend-info {
  display: grid;
  gap: 1rem;
}

.backend-info strong {
  color: #2c3e50;
}

.backend-info p {
  margin: 0.25rem 0 0 0;
  color: #555;
  font-size: 0.95rem;
}

.warning-box ul {
  margin: 0;
  padding-left: 1.5rem;
}

.warning-box li {
  margin: 0.5rem 0;
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

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}
</style>
