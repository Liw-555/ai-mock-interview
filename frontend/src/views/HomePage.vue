<template>
  <AppLayout>
    <div class="home-container">
      <!-- Hero Section -->
      <section class="hero">
        <div class="hero-content">
          <h1 class="hero-title">AI 模拟面试</h1>
          <p class="hero-desc">上传简历，选择岗位，开启 AI 驱动的模拟面试训练。精准出题、实时追问、专业评估，助你斩获心仪 offer。</p>
          <div class="hero-actions">
            <button class="btn btn-primary btn-lg" @click="triggerUpload">
              <svg width="18" height="18" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 2v8m0-8L5 5m3-3l3 3M2 10v2a2 2 0 002 2h8a2 2 0 002-2v-2"/></svg>
              上传简历，快速开始
            </button>
            <router-link to="/history" class="btn btn-secondary btn-lg">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="6"/><path d="M8 5v3l2 2"/></svg>
              查看历史
            </router-link>
          </div>
        </div>
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,.docx"
          style="display: none"
          @change="handleFileChange"
        />
      </section>

      <!-- Upload Progress -->
      <div v-if="uploadProgress" class="upload-progress animate-fade-in">
        <div class="progress-indicator"></div>
        <span>{{ uploadProgress }}</span>
      </div>

      <!-- Libraries Section -->
      <section class="libraries">
        <!-- Position Profiles -->
        <div class="library-card">
          <div class="library-header">
            <div class="library-icon profiles-icon">
              <svg width="20" height="20" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="12" height="12" rx="2"/><path d="M5 6h6M5 9h4"/></svg>
            </div>
            <div>
              <h3 class="library-title">岗位资料库</h3>
              <p class="library-desc">{{ profiles.length }} 个岗位资料</p>
            </div>
          </div>
          <div class="library-items">
            <div
              v-for="p in profiles"
              :key="p.profile_id"
              class="item-card"
              @click="goConfig(p.profile_id)"
            >
              <div class="item-info">
                <span class="item-name">{{ p.target_company }}</span>
                <span class="item-sub">{{ p.target_position }}</span>
              </div>
              <div class="item-actions-group">
                <button class="btn-icon btn-edit" @click.stop="openEditModal(p)" title="编辑">
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M11.5 1.5l3 3L5 14H2v-3L11.5 1.5z"/></svg>
                </button>
                <button class="btn-icon btn-delete" @click.stop="deleteProfile(p.profile_id, p.target_company)" title="删除">
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 4h12M5 4V3a1 1 0 011-1h4a1 1 0 011 1v1M6 7v5M10 7v5M3 4l1 9a1 1 0 001 1h6a1 1 0 001-1l1-9"/></svg>
                </button>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 4l4 4-4 4"/></svg>
              </div>
            </div>
            <button class="item-card item-add" @click="showCreateModal = true">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 3v10M3 8h10"/></svg>
              <span>新建岗位资料</span>
            </button>
          </div>
        </div>

        <!-- Resumes -->
        <div class="library-card">
          <div class="library-header">
            <div class="library-icon resume-icon">
              <svg width="20" height="20" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 2h5l3 3v9a1 1 0 01-1 1H4a1 1 0 01-1-1V3a1 1 0 011-1z"/><path d="M9 2v3h3"/></svg>
            </div>
            <div>
              <h3 class="library-title">简历库</h3>
              <p class="library-desc">{{ resumeStore.resumes.length }} 份简历</p>
            </div>
          </div>
          <div class="library-items">
            <div
              v-for="r in resumeStore.resumes"
              :key="r.resume_id"
              class="item-card"
              @click="goConfigWithResume(r.resume_id)"
            >
              <div class="item-info">
                <span class="item-name">{{ r.original_filename || r.file_path.split(/[/\\]/).pop() }}</span>
                <span :class="['item-sub', r.parsed_at ? 'text-success' : 'text-warning']">
                  {{ r.parsed_at ? '已解析' : '解析中' }}
                </span>
              </div>
              <div class="item-actions-group">
                <button class="btn-icon btn-delete" @click.stop="deleteResume(r.resume_id, r.original_filename)" title="删除">
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 4h12M5 4V3a1 1 0 011-1h4a1 1 0 011 1v1M6 7v5M10 7v5M3 4l1 9a1 1 0 001 1h6a1 1 0 001-1l1-9"/></svg>
                </button>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 4l4 4-4 4"/></svg>
              </div>
            </div>
            <button class="item-card item-add" @click="triggerUpload">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 3v10M3 8h10"/></svg>
              <span>上传新简历</span>
            </button>
          </div>
        </div>
      </section>

      <!-- Drag & Drop overlay -->
      <div
        v-if="isDragging"
        class="drop-overlay"
        @drop.prevent="handleDrop"
        @dragover.prevent
        @dragleave="isDragging = false"
      >
        <div class="drop-content">
          <svg width="48" height="48" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1"><path d="M8 2v8m0-8L5 5m3-3l3 3M2 10v2a2 2 0 002 2h8a2 2 0 002-2v-2"/></svg>
          <p>释放文件以上传简历</p>
          <p class="drop-hint">支持 PDF / Word 格式</p>
        </div>
      </div>

      <!-- Profile Create/Edit Modal -->
      <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeProfileModal">
        <div class="modal animate-slide-up">
          <div class="modal-header">
            <h3>{{ showEditModal ? '编辑岗位资料' : '新建岗位资料' }}</h3>
            <button class="btn btn-ghost modal-close" @click="closeProfileModal">✕</button>
          </div>
          <div class="modal-body">
            <label class="form-label">目标公司</label>
            <input v-model="profileForm.company" class="form-input" placeholder="例如：字节跳动" />
            <label class="form-label">目标岗位</label>
            <input v-model="profileForm.position" class="form-input" placeholder="例如：产品经理" />
            <label class="form-label">岗位 JD</label>
            <textarea v-model="profileForm.jd" class="form-input" placeholder="粘贴岗位描述..." rows="5"></textarea>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeProfileModal">取消</button>
            <button class="btn btn-primary" @click="showEditModal ? updateProfile() : createProfile()">
              {{ showEditModal ? '保存修改' : '保存' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Coming Soon -->
      <section class="coming-soon">
        <div class="coming-soon-inner">
          <svg width="20" height="20" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 4h12v8a2 2 0 01-2 2H4a2 2 0 01-2-2V4zM2 4l2-2h8l2 2"/></svg>
          <span>投递进展追踪 — 即将上线</span>
        </div>
      </section>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useResumeStore } from '../stores/resume.js'
import AppLayout from '../components/AppLayout.vue'

const router = useRouter()
const resumeStore = useResumeStore()
const fileInput = ref(null)
const uploadProgress = ref('')
const profiles = ref([])
const isDragging = ref(false)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingProfileId = ref(null)
const profileForm = ref({ company: '', position: '', jd: '' })

onMounted(() => {
  resumeStore.fetchResumes()
  fetchProfiles()
  // Enable global drag & drop
  document.addEventListener('dragenter', onDragEnter)
  document.addEventListener('dragover', (e) => e.preventDefault())
  document.addEventListener('drop', onGlobalDrop)
})

function onDragEnter(e) {
  e.preventDefault()
  isDragging.value = true
}

function onGlobalDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file && (file.name.endsWith('.pdf') || file.name.endsWith('.docx'))) {
    upload(file)
  }
}

async function fetchProfiles() {
  const res = await fetch('/api/profiles')
  if (res.ok) {
    profiles.value = await res.json()
  }
}

function triggerUpload() {
  fileInput.value?.click()
}

async function handleFileChange(e) {
  const file = e.target.files[0]
  if (file) await upload(file)
}

async function handleDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file) await upload(file)
}

async function upload(file) {
  uploadProgress.value = '正在上传简历...'
  try {
    const resume = await resumeStore.uploadResume(file)
    uploadProgress.value = '解析完成，跳转配置页...'
    setTimeout(() => {
      router.push({
        path: '/config',
        query: { resume_id: resume.resume_id },
      })
    }, 500)
  } catch (err) {
    uploadProgress.value = '上传失败: ' + err.message
  }
}

function goConfig(profileId = null) {
  if (profileId) {
    router.push({ path: '/config', query: { profile_id: profileId } })
  } else {
    router.push('/config')
  }
}

function closeProfileModal() {
  showCreateModal.value = false
  showEditModal.value = false
  editingProfileId.value = null
  profileForm.value = { company: '', position: '', jd: '' }
}

function openEditModal(profile) {
  editingProfileId.value = profile.profile_id
  profileForm.value = {
    company: profile.target_company,
    position: profile.target_position,
    jd: profile.job_description || '',
  }
  showEditModal.value = true
}

async function createProfile() {
  if (!profileForm.value.company || !profileForm.value.position) {
    alert('请至少填写目标公司和目标岗位')
    return
  }
  try {
    const res = await fetch('/api/profiles', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_company: profileForm.value.company,
        target_position: profileForm.value.position,
        job_description: profileForm.value.jd || '暂无JD',
      }),
    })
    if (!res.ok) throw new Error('创建失败')
    const profile = await res.json()
    profiles.value.unshift(profile)
    closeProfileModal()
  } catch (err) {
    alert('创建失败: ' + err.message)
  }
}

async function updateProfile() {
  if (!profileForm.value.company || !profileForm.value.position) {
    alert('请至少填写目标公司和目标岗位')
    return
  }
  try {
    const res = await fetch(`/api/profiles/${editingProfileId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_company: profileForm.value.company,
        target_position: profileForm.value.position,
        job_description: profileForm.value.jd || '暂无JD',
      }),
    })
    if (!res.ok) throw new Error('更新失败')
    const updated = await res.json()
    const idx = profiles.value.findIndex(p => p.profile_id === editingProfileId.value)
    if (idx !== -1) profiles.value[idx] = updated
    closeProfileModal()
  } catch (err) {
    alert('更新失败: ' + err.message)
  }
}

function goConfigWithResume(resumeId) {
  router.push({ path: '/config', query: { resume_id: resumeId } })
}

async function deleteProfile(profileId, companyName) {
  if (!confirm(`确定要删除岗位资料「${companyName}」吗？此操作不可恢复。`)) return
  try {
    const res = await fetch(`/api/profiles/${profileId}`, { method: 'DELETE' })
    if (!res.ok) {
      if (res.status === 409) {
        const data = await res.json()
        alert(data.detail || '该岗位资料关联了面试记录，请先删除相关面试记录')
      } else {
        throw new Error('删除失败')
      }
      return
    }
    profiles.value = profiles.value.filter(p => p.profile_id !== profileId)
  } catch (err) {
    alert('删除失败: ' + err.message)
  }
}

async function deleteResume(resumeId, filename) {
  const displayName = filename || '该简历'
  if (!confirm(`确定要删除简历「${displayName}」吗？此操作不可恢复。`)) return
  try {
    const res = await fetch(`/api/resumes/${resumeId}`, { method: 'DELETE' })
    if (!res.ok) {
      if (res.status === 409) {
        const data = await res.json()
        alert(data.detail || '该简历关联了面试记录，请先删除相关面试记录')
      } else {
        throw new Error('删除失败')
      }
      return
    }
    resumeStore.resumes = resumeStore.resumes.filter(r => r.resume_id !== resumeId)
  } catch (err) {
    alert('删除失败: ' + err.message)
  }
}
</script>

<style scoped>
.home-container {
  max-width: 960px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-6) var(--space-16);
}

/* ── Hero ── */
.hero {
  text-align: center;
  padding: var(--space-16) 0 var(--space-12);
}

.hero-title {
  font-size: var(--text-4xl);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text-primary);
  margin-bottom: var(--space-4);
  background: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-400));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  font-size: var(--text-md);
  color: var(--text-secondary);
  max-width: 520px;
  margin: 0 auto var(--space-8);
  line-height: var(--leading-relaxed);
}

.hero-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
}

/* ── Upload Progress ── */
.upload-progress {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-primary-50);
  border: 1px solid var(--color-primary-200);
  border-radius: var(--radius-lg);
  color: var(--color-primary-700);
  font-size: var(--text-sm);
  font-weight: 500;
  margin-bottom: var(--space-8);
}

.progress-indicator {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-primary-300);
  border-top-color: var(--color-primary-600);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── Libraries ── */
.libraries {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.library-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-xs);
}

.library-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-5);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.library-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
}

.profiles-icon {
  background: var(--color-primary-50);
  color: var(--color-primary-600);
}

.resume-icon {
  background: var(--color-success-50);
  color: var(--color-success-600);
}

.library-title {
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--text-primary);
}

.library-desc {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: 2px;
}

/* ── Library Items ── */
.library-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.item-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--bg-surface);
}

.item-card:hover {
  border-color: var(--color-primary-200);
  background: var(--color-primary-50);
}

.item-card:hover svg {
  color: var(--color-primary-500);
}

.item-card svg {
  color: var(--text-faint);
  flex-shrink: 0;
  transition: color var(--transition-fast);
}

.item-actions-group {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: var(--radius-md);
  background: transparent;
  cursor: pointer;
  color: var(--text-faint);
  transition: all var(--transition-fast);
  opacity: 0;
}

.item-card:hover .btn-icon {
  opacity: 1;
}

.btn-icon.btn-delete:hover {
  background: var(--color-danger-50);
  color: var(--color-danger-600);
}

.btn-icon.btn-edit:hover {
  background: var(--color-primary-50);
  color: var(--color-primary-600);
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.item-name {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-sub {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.text-success { color: var(--color-success-600); }
.text-warning { color: var(--color-warning-600); }

.item-add {
  border-style: dashed;
  color: var(--text-muted);
  justify-content: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
}

.item-add:hover {
  border-color: var(--color-primary-300);
  color: var(--color-primary-600);
}

/* ── Drop Overlay ── */
.drop-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-overlay);
  background: rgba(99, 102, 241, 0.08);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-content {
  text-align: center;
  padding: var(--space-12);
  background: var(--bg-surface);
  border: 2px dashed var(--color-primary-400);
  border-radius: var(--radius-xl);
  color: var(--color-primary-600);
  box-shadow: var(--shadow-xl);
}

.drop-content p {
  font-size: var(--text-lg);
  font-weight: 600;
  margin-top: var(--space-4);
}

.drop-hint {
  font-size: var(--text-sm) !important;
  font-weight: 400 !important;
  color: var(--text-muted) !important;
}

/* ── Coming Soon ── */
.coming-soon {
  margin-top: var(--space-6);
}

/* ── Modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}

.modal {
  background: var(--bg-surface);
  border-radius: var(--radius-xl);
  width: 440px;
  max-width: 90vw;
  box-shadow: var(--shadow-xl);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--border-light);
}

.modal-header h3 {
  font-size: var(--text-lg);
  font-weight: 600;
}

.modal-close {
  padding: var(--space-1);
  font-size: var(--text-md);
  color: var(--text-muted);
}

.modal-body {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
}

.form-input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  background: var(--bg-surface);
  color: var(--text-primary);
  outline: none;
  transition: border-color var(--transition-fast);
  box-sizing: border-box;
}

.form-input:focus {
  border-color: var(--color-primary-400);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border-light);
}

.coming-soon-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-4);
  background: var(--bg-muted);
  border-radius: var(--radius-lg);
  color: var(--text-muted);
  font-size: var(--text-sm);
}

@media (max-width: 640px) {
  .libraries {
    grid-template-columns: 1fr;
  }
  .hero-title {
    font-size: var(--text-2xl);
  }
  .hero-actions {
    flex-direction: column;
  }
}
</style>
