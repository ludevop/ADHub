<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usersApi, type User, type UserCreate, type UserUpdate } from '@/api/users'

const users = ref<User[]>([])
const loading = ref(false)
const error = ref('')

// Modals
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const showPasswordModal = ref(false)
const selectedUser = ref<User | null>(null)

// Create user form
const newUser = ref<UserCreate>({
  username: '',
  password: '',
  given_name: '',
  surname: '',
  email: '',
  description: '',
  must_change_password: true
})

// Edit user form
const editUser = ref<UserUpdate>({
  display_name: '',
  email: '',
  description: '',
  admin_password: ''
})
const editAdminPassword = ref('')

// Password form
const newPassword = ref('')
const mustChangePassword = ref(false)

// Form errors
const createError = ref('')
const createLoading = ref(false)
const editError = ref('')
const editLoading = ref(false)

async function loadUsers() {
  try {
    loading.value = true
    error.value = ''
    const response = await usersApi.listUsers()
    users.value = response.users
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to load users'
    console.error('Error loading users:', e)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  newUser.value = {
    username: '',
    password: '',
    given_name: '',
    surname: '',
    email: '',
    description: '',
    must_change_password: true
  }
  createError.value = ''
  showCreateModal.value = true
}

async function createUser() {
  if (!newUser.value.username || !newUser.value.password) {
    createError.value = 'Username and password are required'
    return
  }

  try {
    createLoading.value = true
    createError.value = ''
    await usersApi.createUser(newUser.value)
    showCreateModal.value = false
    await loadUsers()
  } catch (e: any) {
    createError.value = e.response?.data?.detail || 'Failed to create user'
  } finally {
    createLoading.value = false
  }
}

function openEditModal(user: User) {
  selectedUser.value = user
  editUser.value = {
    display_name: user.display_name || '',
    email: user.email || '',
    description: user.description || '',
    admin_password: ''
  }
  editAdminPassword.value = ''
  editError.value = ''
  showEditModal.value = true
}

async function updateUser() {
  if (!selectedUser.value) return

  if (!editAdminPassword.value) {
    editError.value = 'Administrator password is required to save changes'
    return
  }

  try {
    editLoading.value = true
    editError.value = ''
    await usersApi.updateUser(selectedUser.value.username, {
      display_name: editUser.value.display_name,
      email: editUser.value.email,
      description: editUser.value.description,
      admin_password: editAdminPassword.value
    })
    showEditModal.value = false
    selectedUser.value = null
    editAdminPassword.value = '' // Clear password
    await loadUsers()
  } catch (e: any) {
    editError.value = e.response?.data?.detail || 'Failed to update user'
  } finally {
    editLoading.value = false
  }
}

function openDeleteModal(user: User) {
  selectedUser.value = user
  showDeleteModal.value = true
}

async function deleteUser() {
  if (!selectedUser.value) return

  try {
    await usersApi.deleteUser(selectedUser.value.username)
    showDeleteModal.value = false
    selectedUser.value = null
    await loadUsers()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to delete user'
  }
}

function openPasswordModal(user: User) {
  selectedUser.value = user
  newPassword.value = ''
  mustChangePassword.value = false
  showPasswordModal.value = true
}

async function setPassword() {
  if (!selectedUser.value || !newPassword.value) return

  try {
    await usersApi.setPassword(selectedUser.value.username, {
      new_password: newPassword.value,
      must_change_at_next_login: mustChangePassword.value
    })
    showPasswordModal.value = false
    selectedUser.value = null
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to set password'
  }
}

async function toggleUserStatus(user: User) {
  try {
    if (user.account_disabled) {
      await usersApi.enableUser(user.username)
    } else {
      await usersApi.disableUser(user.username)
    }
    await loadUsers()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to update user status'
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<template>
  <div class="users-page">
    <div class="page-header">
      <div class="header-content">
        <h1>User Management</h1>
        <p class="subtitle">Manage Active Directory users</p>
      </div>
      <button class="btn btn-primary" @click="openCreateModal">
        <span class="icon">➕</span>
        Create User
      </button>
    </div>

    <div v-if="error" class="error-alert">
      <span class="error-icon">⚠️</span>
      <span>{{ error }}</span>
      <button class="close-btn" @click="error = ''">✕</button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading users...</p>
    </div>

    <div v-else-if="users.length === 0" class="empty-state">
      <div class="empty-icon">👥</div>
      <h3>No users found</h3>
      <p>Get started by creating your first user</p>
      <button class="btn btn-primary" @click="openCreateModal">Create User</button>
    </div>

    <div v-else class="users-table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>Username</th>
            <th>Display Name</th>
            <th>Email</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.username" :class="{ disabled: user.account_disabled }">
            <td>
              <div class="username">
                <span class="user-icon">👤</span>
                <strong>{{ user.username }}</strong>
              </div>
            </td>
            <td>{{ user.display_name || '—' }}</td>
            <td>{{ user.email || '—' }}</td>
            <td>
              <span class="status-badge" :class="{ active: !user.account_disabled, disabled: user.account_disabled }">
                {{ user.account_disabled ? 'Disabled' : 'Active' }}
              </span>
            </td>
            <td>
              <div class="actions">
                <button class="action-btn" @click="openEditModal(user)" title="Edit user">
                  ✏️
                </button>
                <button
                  class="action-btn"
                  :class="{ enable: user.account_disabled }"
                  @click="toggleUserStatus(user)"
                  :title="user.account_disabled ? 'Enable user' : 'Disable user'"
                >
                  {{ user.account_disabled ? '✓' : '⊘' }}
                </button>
                <button class="action-btn" @click="openPasswordModal(user)" title="Change password">
                  🔑
                </button>
                <button class="action-btn delete" @click="openDeleteModal(user)" title="Delete user">
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create User Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Create New User</h2>
          <button class="close-btn" @click="showCreateModal = false">✕</button>
        </div>

        <div class="modal-body">
          <div v-if="createError" class="error-alert">
            <span class="error-icon">⚠️</span>
            <span>{{ createError }}</span>
          </div>

          <form @submit.prevent="createUser">
            <div class="form-row">
              <div class="form-group">
                <label for="username">Username *</label>
                <input
                  id="username"
                  v-model="newUser.username"
                  type="text"
                  required
                  :disabled="createLoading"
                  placeholder="e.g., jsmith"
                />
              </div>
              <div class="form-group">
                <label for="password">Password *</label>
                <input
                  id="password"
                  v-model="newUser.password"
                  type="password"
                  required
                  :disabled="createLoading"
                  placeholder="Min. 8 characters"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="given_name">First Name</label>
                <input
                  id="given_name"
                  v-model="newUser.given_name"
                  type="text"
                  :disabled="createLoading"
                  placeholder="John"
                />
              </div>
              <div class="form-group">
                <label for="surname">Last Name</label>
                <input
                  id="surname"
                  v-model="newUser.surname"
                  type="text"
                  :disabled="createLoading"
                  placeholder="Smith"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="email">Email</label>
              <input
                id="email"
                v-model="newUser.email"
                type="email"
                :disabled="createLoading"
                placeholder="john.smith@example.com"
              />
            </div>

            <div class="form-group">
              <label for="description">Description</label>
              <input
                id="description"
                v-model="newUser.description"
                type="text"
                :disabled="createLoading"
                placeholder="User description"
              />
            </div>

            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input
                  v-model="newUser.must_change_password"
                  type="checkbox"
                  :disabled="createLoading"
                />
                <span>Require password change at next login</span>
              </label>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="showCreateModal = false" :disabled="createLoading">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="createLoading">
                <span v-if="createLoading" class="spinner small"></span>
                <span v-else>Create User</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Edit User Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Edit User</h2>
          <button class="close-btn" @click="showEditModal = false">✕</button>
        </div>

        <div class="modal-body">
          <p class="username-display">Editing: <strong>{{ selectedUser?.username }}</strong></p>

          <div v-if="editError" class="error-alert">
            <span class="error-icon">⚠️</span>
            <span>{{ editError }}</span>
          </div>

          <form @submit.prevent="updateUser">
            <div class="form-group">
              <label for="edit_display_name">Display Name</label>
              <input
                id="edit_display_name"
                v-model="editUser.display_name"
                type="text"
                :disabled="editLoading"
                placeholder="John Smith"
              />
            </div>

            <div class="form-group">
              <label for="edit_email">Email</label>
              <input
                id="edit_email"
                v-model="editUser.email"
                type="email"
                :disabled="editLoading"
                placeholder="john.smith@example.com"
              />
            </div>

            <div class="form-group">
              <label for="edit_description">Description</label>
              <input
                id="edit_description"
                v-model="editUser.description"
                type="text"
                :disabled="editLoading"
                placeholder="User description"
              />
            </div>

            <div class="security-notice">
              <span class="security-icon">🔒</span>
              <span>Enter your administrator password to authorize these changes</span>
            </div>

            <div class="form-group">
              <label for="edit_admin_password">Your Administrator Password *</label>
              <input
                id="edit_admin_password"
                v-model="editAdminPassword"
                type="password"
                required
                :disabled="editLoading"
                placeholder="Required to save changes"
              />
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
          <h2>Delete User</h2>
          <button class="close-btn" @click="showDeleteModal = false">✕</button>
        </div>

        <div class="modal-body">
          <p>Are you sure you want to delete user <strong>{{ selectedUser?.username }}</strong>?</p>
          <p class="warning-text">This action cannot be undone.</p>

          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showDeleteModal = false">
              Cancel
            </button>
            <button class="btn btn-danger" @click="deleteUser">
              Delete User
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Password Change Modal -->
    <div v-if="showPasswordModal" class="modal-overlay" @click="showPasswordModal = false">
      <div class="modal small" @click.stop>
        <div class="modal-header">
          <h2>Change Password</h2>
          <button class="close-btn" @click="showPasswordModal = false">✕</button>
        </div>

        <div class="modal-body">
          <p>Change password for <strong>{{ selectedUser?.username }}</strong></p>

          <form @submit.prevent="setPassword">
            <div class="form-group">
              <label for="new_password">New Password</label>
              <input
                id="new_password"
                v-model="newPassword"
                type="password"
                required
                placeholder="Min. 8 characters"
              />
            </div>

            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input v-model="mustChangePassword" type="checkbox" />
                <span>Require password change at next login</span>
              </label>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="showPasswordModal = false">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary">
                Change Password
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.users-page {
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

.users-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table thead {
  background: #f8f9fa;
}

.users-table th {
  text-align: left;
  padding: 1rem;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e0e0e0;
}

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.users-table tr:last-child td {
  border-bottom: none;
}

.users-table tr:hover {
  background: #f8f9fa;
}

.users-table tr.disabled {
  opacity: 0.6;
}

.username {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-icon {
  font-size: 1.25rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.disabled {
  background: #f8d7da;
  color: #721c24;
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

.action-btn.enable {
  background: #d4edda;
  color: #155724;
}

.action-btn.enable:hover {
  background: #c3e6cb;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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
.form-group input[type="email"],
.form-group input[type="password"] {
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
  margin-bottom: 0;
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

.username-display {
  color: #7f8c8d;
  margin-bottom: 1.5rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
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

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .users-table-container {
    overflow-x: auto;
  }

  .users-table {
    min-width: 600px;
  }
}
</style>
