<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { dnsApi, type DNSZone, type DNSRecord, type DNSRecordCreate } from '@/api/dns'

const zones = ref<DNSZone[]>([])
const records = ref<DNSRecord[]>([])
const selectedZone = ref<string>('')
const loading = ref(false)
const recordsLoading = ref(false)
const error = ref('')

// Modals
const showAddRecordModal = ref(false)
const showDeleteModal = ref(false)
const selectedRecord = ref<DNSRecord | null>(null)

// Add record form
const newRecord = ref<DNSRecordCreate>({
  zone: '',
  name: '',
  type: 'A',
  data: '',
  admin_password: ''
})

const deleteAdminPassword = ref('')

// Form errors
const addError = ref('')
const addLoading = ref(false)
const deleteError = ref('')

const recordTypes = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'SRV', 'PTR', 'NS']

const filteredRecords = computed(() => {
  return records.value
})

async function loadZones() {
  try {
    loading.value = true
    error.value = ''
    const response = await dnsApi.listZones()
    zones.value = response.zones

    // Auto-select first zone
    if (zones.value.length > 0 && !selectedZone.value) {
      selectedZone.value = zones.value[0].name
      await loadRecords()
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to load DNS zones'
    console.error('Error loading zones:', e)
  } finally {
    loading.value = false
  }
}

async function loadRecords() {
  if (!selectedZone.value) return

  try {
    recordsLoading.value = true
    error.value = ''
    const response = await dnsApi.listRecords(selectedZone.value)
    records.value = response.records
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to load DNS records'
    console.error('Error loading records:', e)
  } finally {
    recordsLoading.value = false
  }
}

async function onZoneChange() {
  await loadRecords()
}

function openAddRecordModal() {
  newRecord.value = {
    zone: selectedZone.value,
    name: '',
    type: 'A',
    data: '',
    admin_password: ''
  }
  addError.value = ''
  showAddRecordModal.value = true
}

async function addRecord() {
  if (!newRecord.value.name || !newRecord.value.data || !newRecord.value.admin_password) {
    addError.value = 'Name, data, and administrator password are required'
    return
  }

  try {
    addLoading.value = true
    addError.value = ''
    await dnsApi.addRecord(newRecord.value)
    showAddRecordModal.value = false
    await loadRecords()
  } catch (e: any) {
    addError.value = e.response?.data?.detail || 'Failed to add DNS record'
  } finally {
    addLoading.value = false
  }
}

function openDeleteModal(record: DNSRecord) {
  selectedRecord.value = record
  deleteAdminPassword.value = ''
  deleteError.value = ''
  showDeleteModal.value = true
}

async function deleteRecord() {
  if (!selectedRecord.value || !deleteAdminPassword.value) {
    deleteError.value = 'Administrator password is required'
    return
  }

  try {
    await dnsApi.deleteRecord({
      zone: selectedRecord.value.zone,
      name: selectedRecord.value.name,
      type: selectedRecord.value.type,
      data: selectedRecord.value.data,
      admin_password: deleteAdminPassword.value
    })
    showDeleteModal.value = false
    selectedRecord.value = null
    deleteAdminPassword.value = ''
    await loadRecords()
  } catch (e: any) {
    deleteError.value = e.response?.data?.detail || 'Failed to delete DNS record'
  }
}

onMounted(() => {
  loadZones()
})
</script>

<template>
  <div class="dns-page">
    <div class="page-header">
      <div class="header-content">
        <h1>DNS Management</h1>
        <p class="subtitle">Manage Active Directory DNS records</p>
      </div>
      <div class="header-actions">
        <div class="zone-selector">
          <label for="zone-select">Zone:</label>
          <select id="zone-select" v-model="selectedZone" @change="onZoneChange" :disabled="loading">
            <option v-for="zone in zones" :key="zone.name" :value="zone.name">
              {{ zone.name }} ({{ zone.type }})
            </option>
          </select>
        </div>
        <button class="btn btn-primary" @click="openAddRecordModal" :disabled="!selectedZone">
          <span class="icon">➕</span>
          Add Record
        </button>
      </div>
    </div>

    <div v-if="error" class="error-alert">
      <span class="error-icon">⚠️</span>
      <span>{{ error }}</span>
      <button class="close-btn" @click="error = ''">✕</button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading DNS zones...</p>
    </div>

    <div v-else-if="!selectedZone" class="empty-state">
      <div class="empty-icon">🌐</div>
      <h3>No DNS zones found</h3>
      <p>DNS zones are configured automatically with your domain</p>
    </div>

    <div v-else>
      <div v-if="recordsLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading DNS records...</p>
      </div>

      <div v-else-if="records.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <h3>DNS Records</h3>
        <div class="info-notice">
          <span class="info-icon">ℹ️</span>
          <div>
            <p><strong>Note:</strong> Existing DNS records cannot be displayed due to authentication requirements.</p>
            <p>You can add new DNS records, and they will be created successfully in Active Directory.</p>
          </div>
        </div>
        <button class="btn btn-primary" @click="openAddRecordModal">Add DNS Record</button>
      </div>

      <div v-else class="records-table-container">
        <table class="records-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Data</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(record, index) in filteredRecords" :key="index">
              <td>
                <div class="record-name">
                  <span class="record-icon">📝</span>
                  <strong>{{ record.name }}</strong>
                </div>
              </td>
              <td>
                <span class="record-type-badge" :class="`type-${record.type.toLowerCase()}`">
                  {{ record.type }}
                </span>
              </td>
              <td>
                <code class="record-data">{{ record.data }}</code>
              </td>
              <td>
                <div class="actions">
                  <button class="action-btn delete" @click="openDeleteModal(record)" title="Delete record">
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Record Modal -->
    <div v-if="showAddRecordModal" class="modal-overlay" @click="showAddRecordModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Add DNS Record</h2>
          <button class="close-btn" @click="showAddRecordModal = false">✕</button>
        </div>

        <div class="modal-body">
          <div v-if="addError" class="error-alert">
            <span class="error-icon">⚠️</span>
            <span>{{ addError }}</span>
          </div>

          <form @submit.prevent="addRecord">
            <div class="form-group">
              <label for="zone">Zone</label>
              <input
                id="zone"
                v-model="newRecord.zone"
                type="text"
                disabled
                class="zone-display"
              />
            </div>

            <div class="form-group">
              <label for="record_name">Name *</label>
              <input
                id="record_name"
                v-model="newRecord.name"
                type="text"
                required
                :disabled="addLoading"
                placeholder="e.g., www or @ for root"
              />
            </div>

            <div class="form-group">
              <label for="record_type">Type *</label>
              <select
                id="record_type"
                v-model="newRecord.type"
                required
                :disabled="addLoading"
              >
                <option v-for="type in recordTypes" :key="type" :value="type">
                  {{ type }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="record_data">Data *</label>
              <input
                id="record_data"
                v-model="newRecord.data"
                type="text"
                required
                :disabled="addLoading"
                :placeholder="newRecord.type === 'A' ? 'e.g., 192.168.1.10' :
                              newRecord.type === 'AAAA' ? 'e.g., 2001:db8::1' :
                              newRecord.type === 'CNAME' ? 'e.g., server.example.com' :
                              'Record data'"
              />
            </div>

            <div class="security-notice">
              <span class="security-icon">🔒</span>
              <span>Enter your administrator password to authorize this change</span>
            </div>

            <div class="form-group">
              <label for="admin_password">Your Administrator Password *</label>
              <input
                id="admin_password"
                v-model="newRecord.admin_password"
                type="password"
                required
                :disabled="addLoading"
                placeholder="Required to add record"
              />
            </div>

            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="showAddRecordModal = false" :disabled="addLoading">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="addLoading">
                <span v-if="addLoading" class="spinner small"></span>
                <span v-else>Add Record</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="showDeleteModal = false">
      <div class="modal small" @click.stop>
        <div class="modal-header">
          <h2>Delete DNS Record</h2>
          <button class="close-btn" @click="showDeleteModal = false">✕</button>
        </div>

        <div class="modal-body">
          <p>Are you sure you want to delete this DNS record?</p>
          <div class="record-details">
            <p><strong>Name:</strong> {{ selectedRecord?.name }}</p>
            <p><strong>Type:</strong> {{ selectedRecord?.type }}</p>
            <p><strong>Data:</strong> {{ selectedRecord?.data }}</p>
          </div>
          <p class="warning-text">This action cannot be undone.</p>

          <div v-if="deleteError" class="error-alert">
            <span class="error-icon">⚠️</span>
            <span>{{ deleteError }}</span>
          </div>

          <div class="form-group">
            <label for="delete_admin_password">Administrator Password *</label>
            <input
              id="delete_admin_password"
              v-model="deleteAdminPassword"
              type="password"
              required
              placeholder="Required to delete record"
            />
          </div>

          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showDeleteModal = false">
              Cancel
            </button>
            <button class="btn btn-danger" @click="deleteRecord">
              Delete Record
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dns-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1rem;
}

.header-content h1 {
  margin: 0;
  font-size: 2rem;
  color: #2c3e50;
}

.subtitle {
  margin: 0.5rem 0 0 0;
  color: #7f8c8d;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.zone-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.zone-selector label {
  font-weight: 600;
  color: #2c3e50;
}

.zone-selector select {
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
  min-width: 200px;
}

.zone-selector select:focus {
  outline: none;
  border-color: #667eea;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #e0e0e0;
  color: #2c3e50;
}

.btn-secondary:hover:not(:disabled) {
  background: #d0d0d0;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c0392b;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.icon {
  font-size: 1.25rem;
}

.error-alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #fee;
  border-left: 4px solid #e74c3c;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
  color: #c0392b;
}

.error-icon {
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: inherit;
  padding: 0;
  margin-left: auto;
}

.loading-state {
  text-align: center;
  padding: 4rem 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(102, 126, 234, 0.2);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

.spinner.small {
  width: 20px;
  height: 20px;
  border-width: 3px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
}

.empty-state p {
  margin: 0 0 2rem 0;
  color: #7f8c8d;
}

.info-notice {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  background: #e7f3ff;
  border-left: 4px solid #2196f3;
  padding: 1.5rem;
  border-radius: 6px;
  margin: 0 auto 2rem;
  max-width: 600px;
  text-align: left;
}

.info-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.info-notice p {
  margin: 0.5rem 0;
  color: #2c3e50;
  font-size: 0.95rem;
}

.records-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.records-table {
  width: 100%;
  border-collapse: collapse;
}

.records-table thead {
  background: #f8f9fa;
}

.records-table th {
  text-align: left;
  padding: 1rem;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e0e0e0;
}

.records-table td {
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.records-table tr:last-child td {
  border-bottom: none;
}

.records-table tr:hover {
  background: #f8f9fa;
}

.record-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.record-icon {
  font-size: 1.125rem;
}

.record-type-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  background: #e0e0e0;
  color: #2c3e50;
}

.record-type-badge.type-a {
  background: #d4edda;
  color: #155724;
}

.record-type-badge.type-aaaa {
  background: #d1ecf1;
  color: #0c5460;
}

.record-type-badge.type-cname {
  background: #fff3cd;
  color: #856404;
}

.record-type-badge.type-mx {
  background: #f8d7da;
  color: #721c24;
}

.record-type-badge.type-txt {
  background: #e2e3e5;
  color: #383d41;
}

.record-data {
  font-family: 'Courier New', monospace;
  background: #f5f5f5;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  color: #2c3e50;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: #f0f0f0;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
}

.action-btn:hover {
  background: #e0e0e0;
}

.action-btn.delete {
  background: #f8d7da;
  color: #721c24;
}

.action-btn.delete:hover {
  background: #f5c6cb;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal.small {
  max-width: 450px;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
}

.form-group input[type="text"],
.form-group input[type="password"],
.form-group select {
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled,
.form-group select:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.zone-display {
  background: #f8f9fa !important;
  color: #7f8c8d;
  font-weight: 600;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.warning-text {
  color: #e74c3c;
  font-weight: 600;
  margin-top: 0.5rem;
}

.record-details {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  margin: 1rem 0;
}

.record-details p {
  margin: 0.5rem 0;
}

.security-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  border-radius: 6px;
  margin-bottom: 1rem;
  color: #856404;
  font-size: 0.9rem;
}

.security-icon {
  font-size: 1.125rem;
}

@media (max-width: 968px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .zone-selector {
    width: 100%;
  }

  .zone-selector select {
    flex: 1;
  }

  .records-table-container {
    overflow-x: auto;
  }

  .records-table {
    min-width: 700px;
  }
}
</style>
