<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { sharesApi, type Share, type ShareCreate, type ShareUpdate } from '@/api/shares'

const shares = ref<Share[]>([])
const loading = ref(false)
const error = ref('')

// Modals
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const selectedShare = ref<Share | null>(null)

// Create share form
const newShare = ref<ShareCreate>({
  name: '',
  path: '',
  comment: '',
  read_only: false,
  guest_ok: false,
  browseable: true
})

// Edit share form
const editShare = ref<ShareUpdate>({
  path: '',
  comment: '',
  read_only: false,
  guest_ok: false,
  browseable: true
})

// Form errors
const createError = ref('')
const createLoading = ref(false)
const editError = ref('')
const editLoading = ref(false)

async function loadShares() {
  try {
    loading.value = true
    error.value = ''
    const response = await sharesApi.listShares()
    shares.value = response.shares
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to load shares'
    console.error('Error loading shares:', e)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  newShare.value = {
    name: '',
    path: '',
    comment: '',
    read_only: false,
    guest_ok: false,
    browseable: true
  }
  createError.value = ''
  showCreateModal.value = true
}

async function createShare() {
  if (!newShare.value.name || !newShare.value.path) {
    createError.value = 'Share name and path are required'
    return
  }

  try {
    createLoading.value = true
    createError.value = ''
    await sharesApi.createShare(newShare.value)
    showCreateModal.value = false
    await loadShares()
  } catch (e: any) {
    createError.value = e.response?.data?.detail || 'Failed to create share'
  } finally {
    createLoading.value = false
  }
}

function openEditModal(share: Share) {
  selectedShare.value = share
  editShare.value = {
    path: share.path || '',
    comment: share.comment || '',
    read_only: share.read_only,
    guest_ok: share.guest_ok,
    browseable: share.browseable
  }
  editError.value = ''
  showEditModal.value = true
}

async function updateShare() {
  if (!selectedShare.value) return

  try {
    editLoading.value = true
    editError.value = ''
    await sharesApi.updateShare(selectedShare.value.name, editShare.value)
    showEditModal.value = false
    selectedShare.value = null
    await loadShares()
  } catch (e: any) {
    editError.value = e.response?.data?.detail || 'Failed to update share'
  } finally {
    editLoading.value = false
  }
}

function openDeleteModal(share: Share) {
  selectedShare.value = share
  showDeleteModal.value = true
}

async function deleteShare() {
  if (!selectedShare.value) return

  try {
    await sharesApi.deleteShare(selectedShare.value.name)
    showDeleteModal.value = false
    selectedShare.value = null
    await loadShares()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to delete share'
  }
}

onMounted(() => {
  loadShares()
})
</script>

<template>
  <div class="shares-page">
    <div class="page-header">
      <div class="header-content">
        <h1>Share Management</h1>
        <p class="subtitle">Manage Samba file shares</p>
      </div>
      <button class="btn btn-primary" @click="openCreateModal">
        <span class="icon">➕</span>
        Create Share
      </button>
    </div>

    <div v-if="error" class="error-alert">
      <span class="error-icon">⚠️</span>
      <span>{{ error }}</span>
      <button class="close-btn" @click="error = ''">✕</button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading shares...</p>
    </div>

    <div v-else-if="shares.length === 0" class="empty-state">
      <div class="empty-icon">📁</div>
      <h3>No shares found</h3>
      <p>Get started by creating your first share</p>
      <button class="btn btn-primary" @click="openCreateModal">Create Share</button>
    </div>

    <div v-else class="shares-table-container">
      <table class="shares-table">
        <thead>
          <tr>
            <th>Share Name</th>
            <th>Path</th>
            <th>Comment</th>
            <th>Access</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="share in shares" :key="share.name">
            <td>
              <div class="sharename">
                <span class="share-icon">📁</span>
                <strong>{{ share.name }}</strong>
              </div>
            </td>
            <td>
              <code class="path-code">{{ share.path || '—' }}</code>
            </td>
            <td>{{ share.comment || '—' }}</td>
            <td>
              <div class="access-badges">
                <span v-if="share.read_only" class="badge badge-warning">Read-Only</span>
                <span v-else class="badge badge-success">Writable</span>
                <span v-if="share.guest_ok" class="badge badge-info">Guest</span>
              </div>
            </td>
            <td>
              <div class="actions">
                <button class="action-btn" @click="openEditModal(share)" title="Edit share">
                  ✏️
                </button>
                <button class="action-btn delete" @click="openDeleteModal(share)" title="Delete share">
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create Share Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Create New Share</h2>
          <button class="close-btn" @click="showCreateModal = false">✕</button>
        </div>

        <div class="modal-body">
          <div v-if="createError" class="error-alert">
            <span class="error-icon">⚠️</span>
            <span>{{ createError }}</span>
          </div>

          <form @submit.prevent="createShare">
            <div class="form-group">
              <label for="sharename">Share Name *</label>
              <input
                id="sharename"
                v-model="newShare.name"
                type="text"
                required
                :disabled="createLoading"
                placeholder="e.g., Documents"
              />
            </div>

            <div class="form-group">
              <label for="path">Path *</label>
              <input
                id="path"
                v-model="newShare.path"
                type="text"
                required
                :disabled="createLoading"
                placeholder="e.g., /srv/samba/documents"
              />
            </div>

            <div class="form-group">
              <label for="comment">Comment</label>
              <input
                id="comment"
                v-model="newShare.comment"
                type="text"
                :disabled="createLoading"
                placeholder="Share description"
              />
            </div>

            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input
                  v-model="newShare.read_only"
                  type="checkbox"
                  :disabled="createLoading"
                />
                <span>Read-only</span>
              </label>
            </div>

            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input
                  v-model="newShare.guest_ok"
                  type="checkbox"
                  :disabled="createLoading"
                />
                <span>Allow guest access</span>
              </label>
            </div>

            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input
                  v-model="newShare.browseable"
                  type="checkbox"
                  :disabled="createLoading"
                />
                <span>Browseable</span>
              </label>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="showCreateModal = false" :disabled="createLoading">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="createLoading">
                <span v-if="createLoading" class="spinner small"></span>
                <span v-else>Create Share</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Edit Share Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Edit Share</h2>
          <button class="close-btn" @click="showEditModal = false">✕</button>
        </div>

        <div class="modal-body">
          <p class="sharename-display">Editing: <strong>{{ selectedShare?.name }}</strong></p>

          <div v-if="editError" class="error-alert">
            <span class="error-icon">⚠️</span>
            <span>{{ editError }}</span>
          </div>

          <form @submit.prevent="updateShare">
            <div class="form-group">
              <label for="edit_path">Path</label>
              <input
                id="edit_path"
                v-model="editShare.path"
                type="text"
                :disabled="editLoading"
                placeholder="/srv/samba/documents"
              />
            </div>

            <div class="form-group">
              <label for="edit_comment">Comment</label>
              <input
                id="edit_comment"
                v-model="editShare.comment"
                type="text"
                :disabled="editLoading"
                placeholder="Share description"
              />
            </div>

            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input
                  v-model="editShare.read_only"
                  type="checkbox"
                  :disabled="editLoading"
                />
                <span>Read-only</span>
              </label>
            </div>

            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input
                  v-model="editShare.guest_ok"
                  type="checkbox"
                  :disabled="editLoading"
                />
                <span>Allow guest access</span>
              </label>
            </div>

            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input
                  v-model="editShare.browseable"
                  type="checkbox"
                  :disabled="editLoading"
                />
                <span>Browseable</span>
              </label>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="showEditModal = false" :disabled="editLoading">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="editLoading">
                <span v-if="editLoading" class="spinner small"></span>
                <span v-else>Save Changes</span>
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
          <h2>Delete Share</h2>
          <button class="close-btn" @click="showDeleteModal = false">✕</button>
        </div>

        <div class="modal-body">
          <p>Are you sure you want to delete share <strong>{{ selectedShare?.name }}</strong>?</p>
          <p class="warning-text">This action cannot be undone.</p>

          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showDeleteModal = false">
              Cancel
            </button>
            <button class="btn btn-danger" @click="deleteShare">
              Delete Share
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shares-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
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
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.empty-state p {
  margin: 0 0 2rem 0;
  color: #7f8c8d;
}

.shares-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.shares-table {
  width: 100%;
  border-collapse: collapse;
}

.shares-table thead {
  background: #f8f9fa;
}

.shares-table th {
  text-align: left;
  padding: 1rem;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e0e0e0;
}

.shares-table td {
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.shares-table tr:last-child td {
  border-bottom: none;
}

.shares-table tr:hover {
  background: #f8f9fa;
}

.sharename {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.share-icon {
  font-size: 1.25rem;
}

.path-code {
  font-family: 'Courier New', monospace;
  background: #f5f5f5;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  color: #2c3e50;
}

.access-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-success {
  background: #d4edda;
  color: #155724;
}

.badge-warning {
  background: #fff3cd;
  color: #856404;
}

.badge-info {
  background: #d1ecf1;
  color: #0c5460;
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

.form-group input[type="text"] {
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.checkbox-group {
  margin-bottom: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 400;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
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

.sharename-display {
  color: #7f8c8d;
  margin-bottom: 1.5rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .shares-table-container {
    overflow-x: auto;
  }

  .shares-table {
    min-width: 800px;
  }
}
</style>
