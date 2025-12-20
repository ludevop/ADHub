<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { groupsApi, type Group, type GroupCreate, type GroupUpdate } from '@/api/groups'

const groups = ref<Group[]>([])
const loading = ref(false)
const error = ref('')

// Modals
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const showMembersModal = ref(false)
const showAddMemberModal = ref(false)
const selectedGroup = ref<Group | null>(null)

// Create group form
const newGroup = ref<GroupCreate>({
  name: '',
  description: ''
})

// Edit group form
const editGroup = ref<GroupUpdate>({
  description: ''
})

// Add member form
const newMemberUsername = ref('')

// Form errors
const createError = ref('')
const createLoading = ref(false)
const editError = ref('')
const editLoading = ref(false)
const memberError = ref('')
const memberLoading = ref(false)

async function loadGroups() {
  try {
    loading.value = true
    error.value = ''
    const response = await groupsApi.listGroups()
    groups.value = response.groups
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to load groups'
    console.error('Error loading groups:', e)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  newGroup.value = {
    name: '',
    description: ''
  }
  createError.value = ''
  showCreateModal.value = true
}

async function createGroup() {
  if (!newGroup.value.name) {
    createError.value = 'Group name is required'
    return
  }

  try {
    createLoading.value = true
    createError.value = ''
    await groupsApi.createGroup(newGroup.value)
    showCreateModal.value = false
    await loadGroups()
  } catch (e: any) {
    createError.value = e.response?.data?.detail || 'Failed to create group'
  } finally {
    createLoading.value = false
  }
}

function openEditModal(group: Group) {
  selectedGroup.value = group
  editGroup.value = {
    description: group.description || ''
  }
  editError.value = ''
  showEditModal.value = true
}

async function updateGroup() {
  if (!selectedGroup.value) return

  try {
    editLoading.value = true
    editError.value = ''
    await groupsApi.updateGroup(selectedGroup.value.name, {
      description: editGroup.value.description
    })
    showEditModal.value = false
    selectedGroup.value = null
    await loadGroups()
  } catch (e: any) {
    editError.value = e.response?.data?.detail || 'Failed to update group'
  } finally {
    editLoading.value = false
  }
}

function openDeleteModal(group: Group) {
  selectedGroup.value = group
  showDeleteModal.value = true
}

async function deleteGroup() {
  if (!selectedGroup.value) return

  try {
    await groupsApi.deleteGroup(selectedGroup.value.name)
    showDeleteModal.value = false
    selectedGroup.value = null
    await loadGroups()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to delete group'
  }
}

function openMembersModal(group: Group) {
  selectedGroup.value = group
  showMembersModal.value = true
}

function openAddMemberModal() {
  newMemberUsername.value = ''
  memberError.value = ''
  showAddMemberModal.value = true
}

async function addMember() {
  if (!selectedGroup.value || !newMemberUsername.value) return

  try {
    memberLoading.value = true
    memberError.value = ''
    const updatedGroup = await groupsApi.addMember(selectedGroup.value.name, {
      username: newMemberUsername.value
    })
    selectedGroup.value = updatedGroup
    showAddMemberModal.value = false
    await loadGroups()
  } catch (e: any) {
    memberError.value = e.response?.data?.detail || 'Failed to add member'
  } finally {
    memberLoading.value = false
  }
}

async function removeMember(username: string) {
  if (!selectedGroup.value) return

  try {
    const updatedGroup = await groupsApi.removeMember(selectedGroup.value.name, username)
    selectedGroup.value = updatedGroup
    await loadGroups()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to remove member'
  }
}

onMounted(() => {
  loadGroups()
})
</script>

<template>
  <div class="groups-page">
    <div class="page-header">
      <div class="header-content">
        <h1>Group Management</h1>
        <p class="subtitle">Manage Active Directory groups</p>
      </div>
      <button class="btn btn-primary" @click="openCreateModal">
        <span class="icon">➕</span>
        Create Group
      </button>
    </div>

    <div v-if="error" class="error-alert">
      <span class="error-icon">⚠️</span>
      <span>{{ error }}</span>
      <button class="close-btn" @click="error = ''">✕</button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading groups...</p>
    </div>

    <div v-else-if="groups.length === 0" class="empty-state">
      <div class="empty-icon">👥</div>
      <h3>No groups found</h3>
      <p>Get started by creating your first group</p>
      <button class="btn btn-primary" @click="openCreateModal">Create Group</button>
    </div>

    <div v-else class="groups-table-container">
      <table class="groups-table">
        <thead>
          <tr>
            <th>Group Name</th>
            <th>Description</th>
            <th>Members</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="group in groups" :key="group.name">
            <td>
              <div class="groupname">
                <span class="group-icon">👥</span>
                <strong>{{ group.name }}</strong>
              </div>
            </td>
            <td>{{ group.description || '—' }}</td>
            <td>
              <span class="member-count" @click="openMembersModal(group)" :class="{ clickable: group.members.length > 0 }">
                {{ group.members.length }} {{ group.members.length === 1 ? 'member' : 'members' }}
              </span>
            </td>
            <td>
              <div class="actions">
                <button class="action-btn" @click="openMembersModal(group)" title="Manage members">
                  👤
                </button>
                <button class="action-btn" @click="openEditModal(group)" title="Edit group">
                  ✏️
                </button>
                <button class="action-btn delete" @click="openDeleteModal(group)" title="Delete group">
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create Group Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Create New Group</h2>
          <button class="close-btn" @click="showCreateModal = false">✕</button>
        </div>

        <div class="modal-body">
          <div v-if="createError" class="error-alert">
            <span class="error-icon">⚠️</span>
            <span>{{ createError }}</span>
          </div>

          <form @submit.prevent="createGroup">
            <div class="form-group">
              <label for="groupname">Group Name *</label>
              <input
                id="groupname"
                v-model="newGroup.name"
                type="text"
                required
                :disabled="createLoading"
                placeholder="e.g., IT-Staff"
              />
            </div>

            <div class="form-group">
              <label for="description">Description</label>
              <input
                id="description"
                v-model="newGroup.description"
                type="text"
                :disabled="createLoading"
                placeholder="Group description"
              />
            </div>

            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="showCreateModal = false" :disabled="createLoading">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="createLoading">
                <span v-if="createLoading" class="spinner small"></span>
                <span v-else>Create Group</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Edit Group Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Edit Group</h2>
          <button class="close-btn" @click="showEditModal = false">✕</button>
        </div>

        <div class="modal-body">
          <p class="groupname-display">Editing: <strong>{{ selectedGroup?.name }}</strong></p>

          <div v-if="editError" class="error-alert">
            <span class="error-icon">⚠️</span>
            <span>{{ editError }}</span>
          </div>

          <form @submit.prevent="updateGroup">
            <div class="form-group">
              <label for="edit_description">Description</label>
              <input
                id="edit_description"
                v-model="editGroup.description"
                type="text"
                :disabled="editLoading"
                placeholder="Group description"
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
          <h2>Delete Group</h2>
          <button class="close-btn" @click="showDeleteModal = false">✕</button>
        </div>

        <div class="modal-body">
          <p>Are you sure you want to delete group <strong>{{ selectedGroup?.name }}</strong>?</p>
          <p class="warning-text">This action cannot be undone.</p>

          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showDeleteModal = false">
              Cancel
            </button>
            <button class="btn btn-danger" @click="deleteGroup">
              Delete Group
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Members Modal -->
    <div v-if="showMembersModal" class="modal-overlay" @click="showMembersModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Group Members</h2>
          <button class="close-btn" @click="showMembersModal = false">✕</button>
        </div>

        <div class="modal-body">
          <p class="groupname-display">Group: <strong>{{ selectedGroup?.name }}</strong></p>

          <div class="members-header">
            <h3>Members ({{ selectedGroup?.members.length || 0 }})</h3>
            <button class="btn btn-primary btn-small" @click="openAddMemberModal">
              <span class="icon">➕</span>
              Add Member
            </button>
          </div>

          <div v-if="selectedGroup && selectedGroup.members.length === 0" class="empty-state-small">
            <p>No members in this group</p>
          </div>

          <div v-else class="members-list">
            <div v-for="member in selectedGroup?.members" :key="member" class="member-item">
              <span class="member-icon">👤</span>
              <span class="member-name">{{ member }}</span>
              <button class="btn-remove" @click="removeMember(member)" title="Remove member">
                ✕
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Member Modal -->
    <div v-if="showAddMemberModal" class="modal-overlay" @click="showAddMemberModal = false">
      <div class="modal small" @click.stop>
        <div class="modal-header">
          <h2>Add Member</h2>
          <button class="close-btn" @click="showAddMemberModal = false">✕</button>
        </div>

        <div class="modal-body">
          <p>Add user to <strong>{{ selectedGroup?.name }}</strong></p>

          <div v-if="memberError" class="error-alert">
            <span class="error-icon">⚠️</span>
            <span>{{ memberError }}</span>
          </div>

          <form @submit.prevent="addMember">
            <div class="form-group">
              <label for="username">Username</label>
              <input
                id="username"
                v-model="newMemberUsername"
                type="text"
                required
                :disabled="memberLoading"
                placeholder="Enter username"
              />
            </div>

            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="showAddMemberModal = false" :disabled="memberLoading">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="memberLoading">
                <span v-if="memberLoading" class="spinner small"></span>
                <span v-else>Add Member</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.groups-page {
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

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
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

.empty-state-small {
  text-align: center;
  padding: 2rem 1rem;
  color: #7f8c8d;
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

.groups-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.groups-table {
  width: 100%;
  border-collapse: collapse;
}

.groups-table thead {
  background: #f8f9fa;
}

.groups-table th {
  text-align: left;
  padding: 1rem;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e0e0e0;
}

.groups-table td {
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.groups-table tr:last-child td {
  border-bottom: none;
}

.groups-table tr:hover {
  background: #f8f9fa;
}

.groupname {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.group-icon {
  font-size: 1.25rem;
}

.member-count {
  color: #667eea;
  font-weight: 600;
}

.member-count.clickable {
  cursor: pointer;
  text-decoration: underline;
}

.member-count.clickable:hover {
  color: #764ba2;
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

.groupname-display {
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

.members-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.members-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #2c3e50;
}

.members-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  transition: background 0.2s;
}

.member-item:hover {
  background: #e9ecef;
}

.member-icon {
  font-size: 1.125rem;
}

.member-name {
  flex: 1;
  font-weight: 500;
  color: #2c3e50;
}

.btn-remove {
  background: #e74c3c;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.btn-remove:hover {
  background: #c0392b;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .groups-table-container {
    overflow-x: auto;
  }

  .groups-table {
    min-width: 600px;
  }
}
</style>
